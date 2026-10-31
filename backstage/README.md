# Backstage (configuration + skeleton)

Full Backstage is a Yarn monorepo (`@backstage/create-app`); building it needs ~2-4 GB of node_modules and more RAM/time than this 8 GB VM budgets for this project, so the app is delivered as config + template/catalog definitions (see PROGRESS/verification for the honest boundary). The Software Template below is the same golden path the local CLI executes.

Run (on a dev machine): `npx @backstage/create-app@latest`, copy `app-config.yaml`, `catalog-info.yaml` and `templates/` in, register the template location in app-config, `yarn install && yarn start`.
