from typing import Callable, Any, Type

class FunctionLogger:
    
    @classmethod
    def execute(cls, fun: Callable[..., Any], start_msg: str = "", end_msg: str = "", exception: Type[Exception] = None, exception_msg: str = ""):
		
        if start_msg:
            print(start_msg)
        
        if exception is None:
            obj = fun()
        else:
            try:
                obj = fun()
            except exception as e:
                print(f"{exception_msg} {e}")
                return

            
        

        if end_msg:
            print(end_msg)
        
        return obj
    

    