import signal


def timeout(seconds, error_message="Function call timed out"):
    def decorator(func):
        def handler(signum, frame):
            raise TimeoutError(error_message)

        def wrapped(*args, **kwargs):
            # Set the signal handler for SIGALRM
            signal.signal(signal.SIGALRM, handler)
            # Set the alarm to trigger after `seconds` seconds
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                # Cancel the alarm
                signal.alarm(0)
            return result

        return wrapped

    return decorator

# Example usage:

class MyClass:
    @timeout(5)  # Set a timeout of 5 seconds
    def long_running_function(self):
        import time
        time.sleep(6)  # Simulate a function taking longer than the timeout


if __name__ == '__main__':

    try:
        MyClass().long_running_function()
    except TimeoutError as e:
        print(f"Caught TimeoutError: {e}")
