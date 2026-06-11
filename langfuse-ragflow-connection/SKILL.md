---
name: langfuse-ragflow-connection
description: Guide for troubleshooting and resolving connection and telemetry issues between Ragflow and a self-hosted Langfuse instance (specifically addressing Langfuse SDK version conflicts, missing start_generation, and pydantic validation errors).
---

# Langfuse-Ragflow Connection Troubleshooting Guide

This skill provides procedural knowledge for fixing the connection between a self-hosted Langfuse v2.x server and Ragflow.

## The Problem

Ragflow natively integrates with Langfuse for tracing/observability. However, there is a critical known bug in Ragflow's integration code (Issue #14204, reported April 2026):

1. **Missing Method**: Ragflow's core chat functionality relies on calling a `start_generation()` method directly on the `Langfuse` client object. 
2. **SDK Incompatibility**: **No version** of the Langfuse Python SDK (v2.x, v3.x, or v4.x) actually has this method directly on the main client object. 
3. **Cascading Errors**: 
   - Installing SDK **v2.x** triggers a hard crash during error handling (`AttributeError` on `api.core` path).
   - Installing SDK **v3.x or v4.x** triggers Pydantic Validation errors (`ValidationError` on mandatory `organization` or `metadata` fields) because it tries to communicate with a v2.x self-hosted server using v3.x schemas.
   - Even if the SDK is pinned to a specific version (e.g., `3.11.2`) and manually patched to bypass the Pydantic errors, the trace will still fail silently in the background because newer SDKs attempt to use an OpenTelemetry (`/api/public/otel/v1/traces`) endpoint that the v2.x server does not support, resulting in a `404 Not Found`.

## The Solution

Because the bug exists within Ragflow's source code (calling a non-existent SDK method), **manipulating the Langfuse SDK version inside the container will not fix the tracing.**

Until a patch is released by the Ragflow team:

**The only working solution is to disable the Langfuse integration entirely.**

### Instructions for the User

1. Go to the Ragflow UI.
2. Navigate to **Avatar → API → Langfuse Configuration**.
3. Clear/remove the API keys and Host information.
4. Save the configuration.

This stops the broken code from running and allows the chatbot to function normally without throwing errors in the chat interface.
