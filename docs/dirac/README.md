DIRAC Bindings
==============

This subdirectory contains documentation about the provided DIRAC bindings.
The directory [examples](examples/) contains a set of example Python programs showing
practical uses of the bindings.

The API
-------
For using the DIRAC bindings, you need to import `fts3.rest.client.dirac_bindings`, althought
for convenience it can be renamed as something else

```python
import fts3.rest.client.dirac_bindings as fts3
```

In the following code snippets, an import as above is assumed.

### Context
In order to be able to do any operation, some state about the user credentials and remote endpoint need to be
kept.
That's the purpose of a Context

```python
context = fts3.Context(endpoint, user_certificate, user_key)
```

If you are using a proxy certificate, you can either specify only user_certificate, or point both parameters
to the proxy.

user_certificate and user_key can be safely omitted, and the program will use the values
defined in the environment variables `X509_USER_PROXY` or `X509_USER_CERT + X509_USER_KEY`.
