/* eslint-disable @typescript-eslint/no-explicit-any */
/*
 *  Copyright 2021 Collate
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *  http://www.apache.org/licenses/LICENSE-2.0
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

 /**
 * Matillion Connection
 */
export interface MatillionConnection {
    /**
     * Matillion Auth Configuration
     */
    connection?:                 Matillion;
    supportsMetadataExtraction?: boolean;
    /**
     * Service Type
     */
    type?: MatillionType;
}

/**
 * Matillion Auth Configuration
 *
 * Matillion ETL Auth Config
 */
export interface Matillion {
    /**
     * Matillion Host
     */
    hostPort: string;
    /**
     * Password to connect to the Matillion.
     */
    password:   string;
    sslConfig?: Config;
    type?:      Type;
    /**
     * Username to connect to the Matillion. This user should have privileges to read all the
     * metadata in Matillion.
     */
    username: string;
    [property: string]: any;
}

/**
 * Client SSL configuration
 *
 * OpenMetadata Client configured to validate SSL certificates.
 */
export interface Config {
    /**
     * The CA certificate used for SSL validation.
     */
    caCertificate?: string;
    /**
     * The SSL certificate used for client authentication.
     */
    sslCertificate?: string;
    /**
     * The private key associated with the SSL certificate.
     */
    sslKey?: string;
}

export enum Type {
    MatillionETL = "MatillionETL",
}

/**
 * Service Type
 *
 * Service type.
 */
export enum MatillionType {
    Matillion = "Matillion",
}