import threading
from concurrent.futures import ThreadPoolExecutor

class Event:
    def __init__(self, MaxWorkers=4):
        self.Callbacks = []
        self.OnceCallbacks = []
        self.ParallelCallbacks = []
        self.OnceParallelCallbacks = []
        self.Fired = False
        
        self._Lock = threading.Lock()
        self._Executor = ThreadPoolExecutor(max_workers=MaxWorkers)
    
    def Connect(self, Callback):
        with self._Lock:
            self.Callbacks.append(Callback)
    
    def ConnectParallel(self, Callback):
        with self._Lock:
            self.ParallelCallbacks.append(Callback)

    def ConnectOnce(self, Callback):
        with self._Lock:
            self.OnceCallbacks.append(Callback)
    
    def ConnectOnceParallel(self, Callback):
        with self._Lock:
            self.OnceParallelCallbacks.append(Callback)
    
    def Fire(self, *args):
        self.Fired = True
        
        with self._Lock:
            ParallelSnapshot = list(self.ParallelCallbacks + self.OnceParallelCallbacks)
            SerialSnapshot = list(self.Callbacks + self.OnceCallbacks)
            
            self.OnceParallelCallbacks.clear()
            self.OnceCallbacks.clear()
        
        for Callback in ParallelSnapshot:
            try:
                self._Executor.submit(Callback, *args)
            except Exception as e:
                print(f"Error submitting parallel callback: {e}")
        
        for Callback in SerialSnapshot:
            try:
                Callback(*args)
            except Exception as e:
                Name = getattr(Callback, '__name__', str(Callback))
                print(f"Error in serial callback {Name}: {e}")
        
        self.Fired = False
    
    def Shutdown(self):
        self._Executor.shutdown(wait=True)

    def Delete(self):
        self.Shutdown()
        del self
