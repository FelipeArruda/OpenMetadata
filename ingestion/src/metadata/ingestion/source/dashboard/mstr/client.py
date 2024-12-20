#  Copyright 2023 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""
REST Auth & Client for Mstr
"""
import traceback
from typing import List, Optional

import requests

from metadata.generated.schema.entity.services.connections.dashboard.mstrConnection import (
    MstrConnection,
)
from metadata.ingestion.connections.test_connections import SourceConnectionException
from metadata.ingestion.ometa.client import REST, ClientConfig
from metadata.ingestion.source.dashboard.mstr.models import (
    AuthHeaderCookie,
    MstrDashboard,
    MstrDashboardDetails,
    MstrDashboardList,
    MstrProject,
    MstrProjectList,
    MstrSearchResult,
    MstrSearchResultList,
)
from metadata.utils.helpers import clean_uri
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()

API_VERSION = "MicroStrategyLibrary/api"
LOGIN_MODE_GUEST = 8
APPLICATION_TYPE = 35


class MSTRClient:
    """
    Client Handling API communication with Metabase
    """

    def _get_base_url(self, path=None):
        if not path:
            return f"{clean_uri(self.config.hostPort)}/{API_VERSION}"
        return f"{clean_uri(self.config.hostPort)}/{API_VERSION}/{path}"

    def __init__(
        self,
        config: MstrConnection,
    ):
        self.config = config

        self.auth_params: AuthHeaderCookie = self._get_auth_header_and_cookies()

        client_config = ClientConfig(
            base_url=clean_uri(config.hostPort),
            api_version=API_VERSION,
            extra_headers=self.auth_params.auth_header,
            allow_redirects=True,
            cookies=self.auth_params.auth_cookies,
        )

        self.client = REST(client_config)
        self._set_api_session()

    def _get_auth_header_and_cookies(self) -> Optional[AuthHeaderCookie]:
        """
        Send a request to authenticate the user and get headers and

        To know about the data params below please visit
        https://demo.microstrategy.com/MicroStrategyLibrary/api-docs/index.html#/Authentication/postLogin
        """
        try:
            data = {
                "username": self.config.username,
                "password": self.config.password.get_secret_value(),
                "loginMode": LOGIN_MODE_GUEST,
                "applicationType": APPLICATION_TYPE,
            }
            response = requests.post(
                url=self._get_base_url("auth/login"), data=data, timeout=60
            )
            if not response:
                raise SourceConnectionException()
            return AuthHeaderCookie(
                auth_header=response.headers, auth_cookies=response.cookies
            )
        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.error(
                f"Failed to fetch the auth header and cookies due to [{exc}], please validate credentials"
            )
        return None

    def _set_api_session(self) -> bool:
        """
        Set the user api session to active this will keep the connection alive
        """
        api_session = requests.put(
            url=self._get_base_url("sessions"),
            headers=self.auth_params.auth_header,
            cookies=self.auth_params.auth_cookies,
            timeout=60,
        )
        if api_session.ok:
            logger.info(
                f"Connection Successful User {self.config.username} is Authenticated"
            )
            return True
        raise requests.ConnectionError(
            "Connection Failed, Failed to set an api session, Please validate the credentials"
        )

    def close_api_session(self) -> None:
        """
        Closes the active api session
        """
        try:
            close_api_session = self.client.post(
                path="/auth/logout",
            )
            if close_api_session.ok:
                logger.info("API Session Closed Successfully")

        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.warning(f"Failed to close the api sesison due to [{exc}]")

    def is_project_name(self) -> bool:
        return bool(self.config.projectName)

    def get_projects_list(self) -> List[MstrProject]:
        """
        Get List of all projects
        """
        try:
            resp_projects = self.client.get(
                path="/projects",
            )

            project_list = MstrProjectList(projects=resp_projects)
            return project_list.projects

        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.warning(f"Failed to fetch the project list due to [{exc}]")

        return []

    def get_project_by_name(self) -> Optional[MstrProject]:
        """
        Get Project By Name
        """
        try:
            resp_projects = self.client.get(
                path=f"/projects/{self.config.projectName}",
            )

            project = MstrProject.model_validate(resp_projects)
            return project

        except Exception:
            logger.debug(traceback.format_exc())
            logger.warning("Failed to fetch the project list")

        return None

    def get_search_results_list(
        self, project_id, object_type
    ) -> List[MstrSearchResult]:
        """
        Get Search Results

        To know about the data params below please visit
        https://demo.microstrategy.com/MicroStrategyLibrary/api-docs/index.html?#/Browsing/doQuickSearch
        """
        try:
            data = {
                "project_id": project_id,
                "type": object_type,
                "getAncestors": False,
                "offset": 0,
                "limit": -1,
                "certifiedStatus": "ALL",
                "isCrossCluster": False,
                "result.hidden": False,
            }
            resp_results = self.client.get(
                path="/searches/results",
                data=data,
            )

            results_list = MstrSearchResultList.model_validate(resp_results).result
            return results_list

        except Exception:
            logger.debug(traceback.format_exc())
            logger.warning("Failed to fetch the Search Result list")

        return []

    def get_dashboards_list(self, project_id, project_name) -> List[MstrDashboard]:
        """
        Get Dashboard
        """
        try:
            results = self.get_search_results_list(
                project_id=project_id, object_type=55
            )

            dashboards = []
            for result in results:
                dashboards.append(
                    MstrDashboard(projectName=project_name, **result.model_dump())
                )

            dashboards_list = MstrDashboardList(dashboards=dashboards)
            return dashboards_list.dashboards

        except Exception:
            logger.debug(traceback.format_exc())
            logger.warning("Failed to fetch the dashboard list")

        return []

    def get_dashboard_details(
        self, project_id, project_name, dashboard_id
    ) -> Optional[MstrDashboardDetails]:
        """
        Get Dashboard Details
        """
        try:
            headers = {"X-MSTR-ProjectID": project_id} | self.auth_params.auth_header
            resp_dashboard = self.client._request(  # pylint: disable=protected-access
                "GET", path=f"/v2/dossiers/{dashboard_id}/definition", headers=headers
            )

            return MstrDashboardDetails(
                projectId=project_id, projectName=project_name, **resp_dashboard
            )

        except Exception:
            logger.debug(traceback.format_exc())
            logger.warning(f"Failed to fetch the dashboard with id: {dashboard_id}")

        return None
