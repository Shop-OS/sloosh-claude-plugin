# Sloosh for Shopify stores

![Sloosh](assets/sloosh.png)

Sloosh for Shopify stores turns the products in your Shopify store into catalog images, launch ads with copy and short product page videos. It reads your products and your brand, saves a brand kit once, and reuses that brand kit in every request. The pack adds five skills to the core Sloosh plugin: start, brand-kit, catalog-shoot, pdp-video and launch-ads. It reads products and basic shop information only. It never changes your store and never posts to your ad accounts. Claude shows you the quoted credits for each round of work and asks for your approval before it spends.

## What you need

- The core Sloosh plugin, installed and connected to your Sloosh workspace. This pack uses the Sloosh tools from the core plugin.
- A Sloosh workspace with spending enabled. You set the daily allowance in Sloosh settings.
- Optional: a Shopify connector for your store, such as the official Shopify connector at https://setup.shopify.com/mcp. You sign in to your own store to use it. The pack uses only its tools that read products and shop information.
- A store that you own, or the right to use its product images and brand. Claude asks you to confirm this before it imports any images.

Without a Shopify connector, the pack can read the public product pages of your store, or you can paste product page URLs or image URLs.

## Install in Claude Code

Run this in Claude Code:

```
/plugin marketplace add Shop-OS/sloosh-plugin
/plugin install sloosh@sloosh
/plugin install sloosh-shopify@sloosh
```

Then run `/mcp`, select sloosh and sign in to Sloosh to authorize the workspace you want to use. Run `/sloosh-shopify:start` to begin.

## Install in the Claude app

1. In Claude, open Customize, then Plugins. Add the marketplace Shop-OS/sloosh-plugin and install Sloosh for Shopify stores. You can also select Add and Upload plugin, and choose a ZIP of the packs/sloosh-shopify folder.
2. Install the core Sloosh plugin too, if it is not installed yet.
3. Open the plugin's Connectors tab. Select Add if Sloosh is not added yet, then select Connect.
4. Sign in to Sloosh and authorize the workspace you want to use.

On a Team or Enterprise plan, an Owner must add the Sloosh connector for the organization before members can connect.

## Install in Codex

```
codex plugin marketplace add Shop-OS/sloosh-plugin
codex plugin add sloosh@sloosh
codex plugin add sloosh-shopify@sloosh
codex mcp login sloosh
```

## Skills

| Skill | What it makes | Where it runs |
|---|---|---|
| start | A short tour: it checks your connections, finds or makes your brand kit and suggests a first job. | Claude Code, Cowork, Claude app |
| brand-kit | A brand kit file, sloosh-brand.md, with your voice, colours, type, logo, photo style and hero products. | Claude Code, Cowork, Claude app |
| catalog-shoot | Catalog and lifestyle images for several products, in the aspect ratios your channels use. | Claude Code, Cowork, Claude app |
| pdp-video | Short product page videos, made from a start frame for each product. | Claude Code, Cowork, Claude app |
| launch-ads | Ad images and ad copy for a launch, sized for each channel. The pack does not post the ads. | Claude Code, Cowork, Claude app |

## Where the brand kit lives

The brand kit is one file named sloosh-brand.md. Every skill reads the brand kit first. If no brand kit is found, the skill runs the brand-kit flow.

- Claude Code and Cowork: Claude writes sloosh-brand.md at the root of the project folder. Claude suggests a one-line pointer to it in CLAUDE.md, so later sessions find it.
- Claude app: Claude gives you the file. Add it to the Project's knowledge, or save it to memory if memory is on. Claude does not say the brand kit is saved until you add it.

You can also paste the text of a brand kit into a conversation. To change the brand kit, ask Claude to update it. The Updated section records the date and the change.

## Getting products

The pack tries these sources in order and stops at the first one that works:

1. A Shopify connector in the conversation. Claude uses only its tools that read products and shop information.
2. In a coding agent, the Shopify CLI, if it is already set up for your store. Claude uses only a read-only query. Claude does not install the CLI without asking you.
3. In a coding agent that can fetch any URL, the public product data of your storefront. This fails for a store with a password or a headless storefront.
4. Product page URLs or image URLs that you paste. In the Claude app, Claude asks you for these URLs and does not build them itself.

Claude then imports each product image into your Sloosh workspace from its public URL.

## What the pack sends and reads

The pack runs no code on its own. Claude calls the Sloosh server at https://mcp.sloosh.ai/mcp with the prompts, images and choices you give it, using the access you grant when you connect. Sloosh stores the images and videos it makes in your workspace.

When you give a store, Claude fetches public pages of that store's domain and product images from cdn.shopify.com. Through a Shopify connector, Claude reads products and shop information only. The pack never reads orders, customers, discounts or analytics. It never creates, changes or deletes anything in your store, and it does not upload images to your store. It does not post or upload to ad accounts, even when an ads connector is present.

## Spending

Sloosh uses the credits and the daily spending allowance of the workspace you connect. Claude gets a quote for each item before it makes anything. Claude groups the work into rounds. For each round, Claude shows each item with its quoted credits and the round total, and asks for one approval. If the round total is more than the allowance left today, Claude gives you the Sloosh settings link and does not run the round. A video needs a start frame first. If no image fits, Claude makes one in an earlier round, so that video takes two rounds. You set the daily allowance in Sloosh settings. Claude cannot raise it, buy credits or change your plan.

## Example prompts

- "Set up Sloosh for my Shopify store."
- "Make a brand kit for my store from my storefront and my logo."
- "Shoot lifestyle images in 4:5 for the five mugs in my Ceramics collection."
- "Make a short product page video for each product in my new summer collection."
- "Create launch ads with copy for Instagram and TikTok for our new sneaker."

## Support

- Documentation: https://sloosh.ai/docs/mcp
- Support: https://sloosh.ai/docs/support
- Privacy policy: https://sloosh.ai/privacy-policy
- Terms of use: https://sloosh.ai/terms-of-use
