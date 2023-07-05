# Motor Board API Specification
All requests should be sent using these headers (or just use python's `request.[post|get](data=...)`, since that's where I got these headers from):
```json
{
    "Content-Type": "application/x-www-urlencoded",
    "Connection": "keep-alive",
    "Content-Length": "N",
    "Accept-Encoding": "gzip, deflate", 
    "Accept": "*/*"
}
```
Furthermore, all requests return `text/plain`, and all args should be wrapped in strings. If an endpoint is not explicitly stated to return a 2XX code, then it will return 204 unless stated otherwise. All endpoints will return a 400 if required args are missing (or if they're not an expected value), and all args are required unless noted otherwise. Additional arguments will simply be ignored.
All `POST` requests will return 204 unless stated otherwise, and all `GET` requests will return 200 with the request value as a string unless stated otherwise.

# Endpoints

## GET /check-get
Used to make sure GET requests work

## POST /check-post
Used to make sure POST requests work

Args:
* `sample`: anything that can have `std::to_string` called on it

Responses: 
* 200: `arg count: ${len(args)}, 'sample' content: ${sample}`

## GET /get-temp
Reports the temperature of the board

## GET /blink
Makes the onboard LED blink

## POST /change-ip
Changes the IP that the board sends data to. This is stored in persistent memory and doesn't need to be re-set when the board is reset.

Args:
* `ip`: The IP to send data to. Should include `http://` and a port.

<div style="page-break-after: always;"></div>

## POST /give-start-approval
Marks that the motor board is now allowed to start the race (by pressing the appropriate button). Also turns on the green LED. The cars must be marked as ready for this to pass.

Responses:
* 204: Approval has been successfully given
* 400: Approval could not be given, as the cars were not marked as ready

## POST /force-spin-motor
Forces the motor to spin with or without the cars being marked ready (and without approval).

Args:
* `silent`: Optional. Just the existence of the arg is checked, so the value doesn't matter. If this argument is included, the POST request to the backend's `/run-started` endpoint is not sent.