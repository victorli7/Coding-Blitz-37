## Get Started

This guide describes how to deploy this Flask application to [DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform).

This repo is a fork of [digitalocean/sample-flask](https://github.com/digitalocean/sample-flask).

**Note**: Following these steps may result in charges for the use of DigitalOcean services.

### Requirements

* You need a DigitalOcean account. If you do not already have one, first [sign up](https://cloud.digitalocean.com/registrations/new).

## Deploy the App

Click the following button to deploy this repo to App Platform. If you are not currently logged in with your DigitalOcean account, this button prompts you to log in.

[![Deploy to DigitalOcean](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/victorli7/Coding-Blitz-37/tree/main)

Pushes to the `main` branch automatically redeploy the app when **Autodeploy** is enabled.

Alternatively, visit the [control panel](https://cloud.digitalocean.com/apps) and click **Create App**. Under **Service Provider**, select **GitHub**, then choose **victorli7/Coding-Blitz-37**. Set the branch to **main** and ensure **Autodeploy** is checked, then click **Next**.

After starting the deploy, follow these steps:

1. Configure the app, such as by specifying HTTP routes, declaring environment variables, or adding a database. For the purposes of this tutorial, this step is optional.
1. Provide a name for your app and select the region to deploy your app to, then click **Next**. By default, App Platform selects the region closest to you. Unless your app needs to interface with external services, your chosen region does not affect the app's performance, since all App Platform apps are routed through a global CDN.
1. On the following screen, leave all the fields as they are and click **Next**.
1. Confirm your plan settings and how many containers you want to launch and click **Launch Basic/Pro App**.

After, you should see a "Building..." progress indicator. You can click **View Logs** to see more details of the build. It can take a few minutes for the build to finish, but you can follow the progress in the **Deployments** tab.

Once the build completes successfully, click the **Live App** link in the header and you should see your running application in a new tab, displaying the home page.


## Make Changes to Your App

Pushing a new change to `main` automatically redeploys the app to App Platform with zero downtime.

Here's an example code change you can make for this app:

1. Edit `templates/index.html` and replace "Welcome to your new Flask App!" with a different greeting
1. Commit the change to the `main` branch. Normally it's a better practice to create a new branch for your change and then merge that branch to `main` after review, but for this demo you can commit to the `main` branch directly.
1. Visit the [control panel](https://cloud.digitalocean.com/apps) and navigate to your app.
1. You should see a "Building..." progress indicator, just like when you first created the app.
1. Once the build completes successfully, click the **Live App** link in the header and you should see your updated application running. You may need to force refresh the page in your browser (e.g. using **Shift** + **Reload**).

## Learn More

To learn more about App Platform and how to manage and update your application, see [our App Platform documentation](https://www.digitalocean.com/docs/app-platform/).

## Delete the App

When you no longer need this application running live, you can delete it by following these steps:
1. Visit the [Apps control panel](https://cloud.digitalocean.com/apps).
2. Navigate to the app.
3. In the **Settings** tab, click **Destroy**.

**Note**: If you do not delete your app, charges for using DigitalOcean services will continue to accrue.
