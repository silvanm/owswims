FROM node:14

COPY package.json yarn.lock ./

ENV PATH="./node_modules/.bin:$PATH"

ARG GOOGLE_MAPS_KEY
ARG GRAPHQL_ENDPOINT

COPY . ./

RUN yarn install

RUN nuxt build

ENV HOST 0.0.0.0

EXPOSE 3000

CMD [ "nuxt", "start" ]
