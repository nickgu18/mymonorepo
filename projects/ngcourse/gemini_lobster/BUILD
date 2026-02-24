load("//devtools/python/blaze:strict.bzl", "py_strict_binary", "py_strict_library", "py_strict_test")

package(default_visibility = ["//visibility:public"])

py_strict_library(
    name = "gemini_chat_bridge_utils",
    srcs = [
        "__init__.py",
        "utils.py",
    ],
    deps = [
        "//third_party/py/google/auth:transport/requests",
        "//third_party/py/google/oauth2:credentials",
        "//third_party/py/google_auth_oauthlib",
        "//third_party/py/googleapiclient",
    ],
)

py_strict_library(
    name = "gemini_chat_bridge_hooks_lib",
    srcs = [
        "hooks/__init__.py",
        "hooks/chat_hook.py",
    ],
    deps = [
        ":gemini_chat_bridge_utils",
        "//third_party/py/googleapiclient",
    ],
)

py_strict_library(
    name = "gemini_chat_bridge_daemon_lib",
    srcs = [
        "chat_bridge_daemon.py",
    ],
    deps = [
        ":gemini_chat_bridge_utils",
        "//third_party/py/googleapiclient",
    ],
)

py_strict_binary(
    name = "gemini_chat_bridge_daemon",
    srcs = ["chat_bridge_daemon.py"],
    main = "chat_bridge_daemon.py",
    deps = [
        ":gemini_chat_bridge_daemon_lib",
        ":gemini_chat_bridge_utils",
        "//third_party/py/googleapiclient:googleapiclient_gce_no_cache",
    ],
)

py_strict_binary(
    name = "gemini_chat_hook",
    srcs = ["hooks/chat_hook.py"],
    main = "hooks/chat_hook.py",
    deps = [
        ":gemini_chat_bridge_hooks_lib",
        ":gemini_chat_bridge_utils",
        "//third_party/py/googleapiclient:googleapiclient_gce_no_cache",
    ],
)

py_strict_test(
    name = "test_utils",
    srcs = ["tests/test_utils.py"],
    deps = [
        ":gemini_chat_bridge_utils",
    ],
)

py_strict_test(
    name = "test_daemon",
    srcs = ["tests/test_daemon.py"],
    deps = [
        ":gemini_chat_bridge_daemon_lib",
        ":gemini_chat_bridge_utils",
    ],
)

py_strict_test(
    name = "test_hooks",
    srcs = ["tests/test_hooks.py"],
    deps = [
        ":gemini_chat_bridge_hooks_lib",
        ":gemini_chat_bridge_utils",
        "//third_party/py/googleapiclient:googleapiclient_gce_no_cache",
    ],
)

py_strict_test(
    name = "test_hooks_error",
    srcs = ["tests/test_hooks_error.py"],
    deps = [
        ":gemini_chat_bridge_hooks_lib",
        ":gemini_chat_bridge_utils",
    ],
)

py_strict_test(
    name = "test_args_parsing",
    srcs = ["tests/test_args_parsing.py"],
    deps = [
        ":gemini_chat_bridge_daemon_lib",
    ],
)

py_strict_test(
    name = "test_integration",
    srcs = ["tests/test_integration.py"],
    deps = [
        ":gemini_chat_bridge_daemon_lib",
        ":gemini_chat_bridge_hooks_lib",
        ":gemini_chat_bridge_utils",
    ],
)
