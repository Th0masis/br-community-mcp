# End-to-End Tests

This directory is reserved for end-to-end tests that would test the MCP server with real API calls to the B&R Community forum.

E2E tests are currently not implemented, as they would require:
- Real network requests to the B&R Community API
- Handling rate limits and network reliability
- Managing test data on the live forum

Consider implementing E2E tests when:
- Testing against a staging/test instance of the forum
- Implementing smoke tests for critical functionality
- Validating the complete workflow from MCP client to API response
