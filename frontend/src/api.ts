
import { useState, useEffect, useCallback } from 'react';
import { File, Class, Method, Call, ComponentRelationship, QueryResponse, StatusUpdate } from './types';

const API_BASE = '/api';

export const useApi = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [classes, setClasses] = useState<Class[]>([]);
  const [methods, setMethods] = useState<Method[]>([]);
  const [calls, setCalls] = useState<Call[]>([]);
  const [components, setComponents] = useState<ComponentRelationship[]>([]);
  const [status, setStatus] = useState<StatusUpdate | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [filesRes, classesRes, methodsRes, callsRes, componentsRes] = await Promise.all([
        fetch(`${API_BASE}/files`),
        fetch(`${API_BASE}/classes`),
        fetch(`${API_BASE}/methods`),
        fetch(`${API_BASE}/calls`),
        fetch(`${API_BASE}/components`),
      ]);

      setFiles(await filesRes.json());
      setClasses(await classesRes.json());
      setMethods(await methodsRes.json());
      setCalls(await callsRes.json());
      setComponents(await componentsRes.json());
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }, []);

  const sendQuery = useCallback(async (question: string): Promise<QueryResponse> => {
    const response = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    return await response.json();
  }, []);

  useEffect(() => {
    fetchData();

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/status`;
    const websocket = new WebSocket(wsUrl);

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStatus(data);
      if (data.type === 'file_changed' || data.type === 'sync_complete') {
        fetchData();
      }
    };

    return () => {
      websocket.close();
    };
  }, [fetchData]);

  return {
    files,
    classes,
    methods,
    calls,
    components,
    status,
    fetchData,
    sendQuery,
  };
};
