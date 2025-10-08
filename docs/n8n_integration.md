# N8N Integration with Open Water Swims GraphQL API

This guide explains how to authenticate with the Open Water Swims GraphQL API using N8N.

## Authentication Methods

The API supports two authentication methods:

1. **GraphQL Mutation (Original)**: Using the `tokenAuth` mutation to obtain a JWT token
2. **Header Authentication (New)**: Using API tokens in the request header

## Using Header Authentication with N8N

Header Authentication is the recommended method for N8N integration as it's supported natively.

### Step 1: Generate an API Token

First, generate an API token using the GraphQL mutation:

```graphql
mutation {
  createApiToken(name: "N8N Integration") {
    success
    token
    error
  }
}
```

Response:
```json
{
  "data": {
    "createApiToken": {
      "success": true,
      "token": "your-long-api-token-here",
      "error": null
    }
  }
}
```

Save this token securely.

### Step 2: Configure N8N

1. In N8N, add a new **HTTP Request** node
2. Configure the node:
   - Method: `POST`
   - URL: `https://open-water-swims.com/graphql`
   - Authentication: **Header Auth**
   - Header Auth Parameters:
     - Name: `Authorization`
     - Value: `Token your-long-api-token-here`

3. Set the request body:
   - Content-Type: `application/json`
   - Body:
     ```json
     {
       "query": "query { allOrganizers { edges { node { id name } } } }"
     }
     ```

### Example N8N HTTP Request Node Configuration

- **Authentication Tab**:
  - Authentication: Header Auth
  - Header Auth Parameters:
    - Name: `Authorization`
    - Value: `Token your-long-api-token-here`

- **Options Tab**:
  - Method: POST
  - URL: https://open-water-swims.com/graphql
  - Body Content Type: JSON
  - Body:
    ```json
    {
      "query": "query { allOrganizers { edges { node { id name } } } }"
    }
    ```

### Processing the Response

The GraphQL API will return data in the following format:

```json
{
  "data": {
    "allOrganizers": {
      "edges": [
        {
          "node": {
            "id": "T3JnYW5pemVyTm9kZTox",
            "name": "Example Organizer"
          }
        },
        ...
      ]
    }
  }
}
```

Use the N8N JSON node to extract and process this data as needed for your workflow.

## Managing API Tokens

### View Your Tokens

You can view all your existing API tokens with this query:

```graphql
query {
  myApiTokens {
    id
    name
    createdAt
    lastUsedAt
  }
}
```

### Delete a Token

If you need to revoke a token, use the following mutation:

```graphql
mutation {
  deleteApiToken(tokenId: "TokenID") {
    success
    error
  }
}
```

Note: Replace `TokenID` with the actual ID from the `myApiTokens` query result.

## Security Notes

- Keep your API token secure; it grants access to your account resources
- If you suspect a token has been compromised, you can revoke it in the admin interface or create a new token and stop using the old one
- Consider setting an appropriate name for each token to track their usage

## Example GraphQL Queries

The API supports various queries:

```graphql
# Get all events
query {
  allEvents {
    edges {
      node {
        id
        name
        startDate
      }
    }
  }
}

# Get locations
query {
  allLocations {
    edges {
      node {
        id
        name
        city
        country
      }
    }
  }
}
``` 