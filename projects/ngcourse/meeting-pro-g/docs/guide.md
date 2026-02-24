To resolve this issue:

If a service account invokes your Cloud Run service, set the audience claim (aud) of the Google-signed ID token to the following:

If you set the aud to the URL of the receiving service using the format https://SERVICE.run.app or https://REGION-PROJECT_ID.cloudfunctions.net/FUNCTION, your service must require authentication. Invoke your Cloud Run service using the Cloud Run URL or through a load balancer URL. For examples on sending authenticated requests, see Invoke with an HTTPS request.

If you set the aud to the Client ID of an OAuth 2.0 Client ID with type Web application, using the format nnn-xyz.apps.googleusercontent.com, you can invoke your Cloud Run service through an HTTPS load balancer secured by IAP. We recommend this approach for an Application Load Balancer backed by multiple Cloud Run services in different regions.

If you set the aud to a configured custom audience, use the exact values provided. For example, if the custom audience is https://service.example.com, the audience claim value must also be https://service.example.com.

Make sure that your requests include an Authorization: Bearer ID_TOKEN header, or an X-Serverless-Authorization: Bearer ID_TOKEN header for custom authorization, and that the token is an ID token, not an access or refresh token. A 401 error might occur in the following scenarios due to incorrect authorization format:

The authorization token uses an invalid format.

The authorization header isn't a JSON Web Token (JWT) with a valid signature.

The authorization header contains multiple JWTs.

Multiple authorization headers are present in the request.

To check claims on a JWT, use the jwt.io tool.

If you get invalid tokens when using the metadata server to fetch ID and access tokens to authenticate requests with the Cloud Run service or job identity with an HTTP proxy to route egress traffic, add the following hosts to the HTTP proxy exceptions:

169.254.* or 169.254.0.0/16

*.google.internal

A 401 error commonly occurs when Cloud Client Libraries use the metadata server to fetch Application Default Credentials to authenticate REST or gRPC invocations. If you don't define the HTTP proxy exceptions, the following behavior results:

If different Google Cloud workloads host a Cloud Run service or job and the HTTP proxy, even if the Cloud Client Libraries fetch the credentials, the service account that's assigned to the HTTP proxy workload generates the tokens. The tokens might not have the required permissions to perform the intended Google Cloud API operations. This is because the service account fetches the tokens from the view of the HTTP proxy workload's metadata server, instead of the Cloud Run service or job.

If the HTTP proxy isn't hosted in Google Cloud, and you route metadata server requests using the proxy, then the token requests fail and the Google Cloud APIs operations don't authenticate.

Redeploy your service to allow public access if this is supported by your organization. This is useful for testing.


