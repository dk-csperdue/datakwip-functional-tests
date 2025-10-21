### Functional Tests Setup

This is a PROMPT to give you a set of steps in order to establish a simple functional test that allows you quickly test that all components of the datakwip-platform in Railways is able to:

(1)  Successfully authenticate via Oauth.
(2)  Work (where required) with both internal and external network routes.
(3)  Access data in the appropriate database.

### Notes
- This test is NOT comprehensive.  It is a quick test to make sure all services, auth, database, and routes are working.
- We will run this test frequently so it should not take long to execute.
- The test will be designed progressively to test shorter data flows and then longer data flows.
- All tests should connect to the Railways environment

### Setup: These are steps you only need to take once to prepare for the test.  
(1)  In this directory /datakwip-function-tests, establish a new subrepository.
(2)  Create a new subrepository in github.
(3)  Create a new API client in python that can connect directly to datakwip-api in railway via the Public URL.  Choose a simple api call that requires an auth scope (i.e. not the health endpoint) and send a query, make sure you get a valid response with database data from the datakwip-timescaledb instance in railways.  Ensure the API client is exctensible with more test calls, but only add one for now.
(4)  Create a basic MCP Client in python that can connect directly to datakwip-mcp-connect in railway via the public URL.  Send an MCP tool call that causes an API call to be invoked in datakwip-api.  Ensure data is returned from datakwip-timescaledb.  Ensure the MCP client is extensible with more test calls, but only add one for now.
(5)  Using Browser MCP, connect to datakwip-ai-ui, login to Data Explorer and execute a query, verify that we get data from datakwip-timescaledb.  Now write a programmatic test that can execute this workflow without using Browser MCP via code.
(6)  Ensure we can access and log into the keycloak admin console via the public URL using Browser MCP.  Then develop a programmtic test that can execute this workflow.

### Deliverable
The final deliverable is a single, stage programmatic test that ensures all of these flows ar eoperational.  I will run this test each day before starting work and when we are done for the day so we make sure there are no surprises!

Please let me know your thoughts if you feel there are any other steps we should add to accomplish this goal.  