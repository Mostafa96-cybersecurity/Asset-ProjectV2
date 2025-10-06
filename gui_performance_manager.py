
import threading
import concurrent.futures
from typing import List, Callable

class GUIPerformanceManager:
    """Multithreaded performance manager for GUI"""
    
    def __init__(self, gui_app=None):
        self.gui_app = gui_app
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=8)
        self.active_threads = []
    
    def run_parallel_collection(self, collection_functions: List[Callable], max_workers=4):
        """Run multiple collection functions in parallel"""
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all collection tasks
                futures = []
                for func in collection_functions:
                    future = executor.submit(func)
                    futures.append(future)
                
                # Wait for completion
                results = []
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result(timeout=300)  # 5 minute timeout
                        results.append(result)
                    except Exception as e:
                        results.append(f"Error: {e}")
                
                return results
                
        except Exception as e:
            if self.gui_app and hasattr(self.gui_app, 'log_output'):
                self.gui_app.log_output.append(f"Parallel collection error: {e}")
            return []
    
    def run_background_task(self, task_function, *args, **kwargs):
        """Run task in background without blocking GUI"""
        def task_wrapper():
            try:
                return task_function(*args, **kwargs)
            except Exception as e:
                if self.gui_app and hasattr(self.gui_app, 'log_output'):
                    self.gui_app.log_output.append(f"Background task error: {e}")
        
        thread = threading.Thread(target=task_wrapper, daemon=True)
        thread.start()
        self.active_threads.append(thread)
        return thread
    
    def get_performance_stats(self):
        """Get performance statistics"""
        active_count = threading.active_count()
        thread_count = len(self.active_threads)
        
        return {
            'active_threads': active_count,
            'managed_threads': thread_count,
            'thread_pool_size': self.thread_pool._max_workers,
            'performance_mode': 'High Performance Multithreading'
        }

# Global performance manager
gui_performance_manager = None

def get_gui_performance_manager(gui_app=None):
    """Get GUI performance manager"""
    global gui_performance_manager
    if gui_performance_manager is None:
        gui_performance_manager = GUIPerformanceManager(gui_app)
    return gui_performance_manager
