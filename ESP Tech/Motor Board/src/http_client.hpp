#ifndef HTTP_CLIENT_WRAPPER
#define HTTP_CLIENT_WRAPPER

#include <inttypes.h>

/// Wraps an HTTP client which allows sending GET and POST requests
class HTTPClientWrapper {
   public:
    /// Sends a GET request to the given URL
    /// @param url The URL to send the GET request to
    /// @param silenceDebug Whether to silence debug output (useful for check-connectivity)
    static bool get(String url, bool silenceDebug = false);

    /// Sends a plaintext POST request to the given URL
    /// @param url The URL to send the POST request to
    /// @param body The string to pass with the POST request
    /// @param silenceDebug Whether to silence debug output (useful for check-connectivity)
    static bool post(String url, const char* body = "", bool silenceDebug = false);
};

#endif  // HTTP_CLIENT_WRAPPER