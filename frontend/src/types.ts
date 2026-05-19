
export interface File {
  id: number;
  path: string;
  hash: string;
  created_at: string;
  updated_at: string;
}

export interface Class {
  id: number;
  name: string;
  file_id: number;
  flags: number;
}

export interface Method {
  id: number;
  name: string;
  class_id: number;
}

export interface Call {
  caller_id: number;
  callee_id: number;
}

export interface ComponentRelationship {
  parent_id: number;
  child_id: number;
}

export interface QueryResponse {
  sql: string;
  result: any[];
  error?: string;
}

export interface StatusUpdate {
  type: string;
  payload: any;
}
