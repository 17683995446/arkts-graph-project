
import os
import time
import threading
from typing import List, Tuple, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
import arkts_analyzer

class ChangeQueue:
    def __init__(self, debounce_ms: int = 1000):
        self.queue: List[Tuple[str, str]] = []
        self.debounce_ms = debounce_ms
        self.lock = threading.Lock()
        self.last_update_time = 0.0
        self.processing_thread: threading.Thread | None = None
        self.running = False
        self.callback = None
    
    def add_change(self, file_path: str, event_type: str):
        with self.lock:
            normalized_path = os.path.normpath(file_path)
            if normalized_path.endswith('.ets'):
                self.queue = [(p, t) for p, t in self.queue if p != normalized_path]
                self.queue.append((normalized_path, event_type))
                self.last_update_time = time.time()
    
    def start_processing(self, callback):
        self.running = True
        self.callback = callback
        self.processing_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.processing_thread.start()
    
    def stop_processing(self):
        self.running = False
        if self.processing_thread:
            self.processing_thread.join()
    
    def _process_loop(self):
        while self.running:
            time.sleep(0.1)
            with self.lock:
                if self.queue and time.time() - self.last_update_time > self.debounce_ms / 1000:
                    changes = self.queue.copy()
                    self.queue.clear()
                else:
                    changes = []
            
            if changes and self.callback:
                for file_path, event_type in changes:
                    try:
                        if event_type in ['created', 'modified']:
                            if os.path.exists(file_path):
                                arkts_analyzer.update_file_knowledge_graph(file_path)
                                self.callback('file_changed', {'path': file_path, 'type': event_type})
                        elif event_type == 'deleted':
                            pass
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

class ArkTSFileHandler(FileSystemEventHandler):
    def __init__(self, change_queue: ChangeQueue):
        self.change_queue = change_queue
    
    def on_modified(self, event):
        if not event.is_directory:
            self.change_queue.add_change(event.src_path, 'modified')
    
    def on_created(self, event):
        if not event.is_directory:
            self.change_queue.add_change(event.src_path, 'created')
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.change_queue.add_change(event.src_path, 'deleted')

class FileMonitorService:
    def __init__(self, project_path: str, debounce_ms: int = 1000):
        self.project_path = project_path
        self.change_queue = ChangeQueue(debounce_ms)
        self.observer = Observer()
        self.handler = ArkTSFileHandler(self.change_queue)
        self.status_callbacks: List = []
    
    def start(self, status_callback=None):
        if status_callback:
            self.status_callbacks.append(status_callback)
            self.change_queue.start_processing(status_callback)
        
        self.observer.schedule(self.handler, self.project_path, recursive=True)
        self.observer.start()
        
        for callback in self.status_callbacks:
            callback('monitor_started', {'path': self.project_path})
    
    def stop(self):
        self.observer.stop()
        self.observer.join()
        self.change_queue.stop_processing()
        
        for callback in self.status_callbacks:
            callback('monitor_stopped', {})
    
    def initial_sync(self):
        count = 0
        total = 0
        
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.ets'):
                    total += 1
        
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.ets'):
                    file_path = os.path.join(root, file)
                    try:
                        arkts_analyzer.update_file_knowledge_graph(file_path)
                        count += 1
                        progress = (count / total) * 100 if total > 0 else 100
                        for callback in self.status_callbacks:
                            callback('sync_progress', {'count': count, 'total': total, 'progress': progress})
                    except Exception as e:
                        print(f"Error syncing {file_path}: {e}")
        
        for callback in self.status_callbacks:
            callback('sync_complete', {'count': count})
