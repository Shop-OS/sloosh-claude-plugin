# Sloosh for Claude

![Sloosh](assets/sloosh.png)

Sloosh makes product images, ad variants and short product videos, and runs the published Sloosh Spaces in your workspace. This plugin connects Claude to your Sloosh workspace and adds six skills: product imagery, ad variants, published Spaces, product video, UGC storyboards and launch films.

Sloosh uses the credits and the daily spending allowance of the workspace you connect. Claude shows you the quoted credits and asks for your approval. Sloosh blocks paid calls above your "Ask before spending more than" amount until you approve. You set the daily allowance in Sloosh settings. Claude cannot raise it, buy credits or change your plan.

## Install in Claude Code

Run this in Claude Code:

```
/plugin install sloosh --marketplace Shop-OS/sloosh-claude-plugin
```

On an older Claude Code, add the marketplace first:

```
/plugin marketplace add Shop-OS/sloosh-claude-plugin
/plugin install sloosh@sloosh
```

Then run `/mcp`, select sloosh and sign in to Sloosh to authorize the workspace you want to use.

## Install in the Claude app

1. Download the Sloosh plugin ZIP from the Sloosh MCP page.
2. In Claude, open Customize, then Plugins, then select Add and Upload plugin. Choose the ZIP.
3. Open the plugin's Connectors tab. Select Add if Sloosh is not added yet, then select Connect.
4. Sign in to Sloosh and authorize the workspace you want to use.

On a Team or Enterprise plan, an Owner must add the Sloosh connector for the organization before members can connect.

## Use the connector without the plugin

You can also add Sloosh as a custom connector. In Claude, open Customize, then Connectors, and add a custom connector with this URL: https://mcp.sloosh.ai/mcp. Sign in to Sloosh and authorize your workspace. You get the Sloosh tools without the six skills.

## Launch films

The launch film skill directs and renders a SaaS or product launch film with Remotion on your computer, cut to your voiceover. It runs in Claude Code, or wherever Claude can run commands on your computer. It needs Node.js, ffmpeg, and Python 3 with numpy and Pillow. It transcribes the voiceover with whisper-cpp, which it installs with Homebrew on macOS after it asks you. It can use Sloosh images and clips for missing shots after you approve each quote. Remotion is free for individuals, non-profits and for-profit companies with up to three employees. Larger for-profit companies need a Remotion company license.

## What the plugin sends

The plugin runs no code on its own. The launch film skill includes scripts and a Remotion project template that run on your computer only when you ask for a film. Claude calls the Sloosh server at https://mcp.sloosh.ai/mcp with the prompts, images and choices you give it, using the access you grant when you connect. Sloosh stores the images and videos it makes in your workspace.

## Example prompts

- "Make a studio photo of my water bottle on a clean white background."
- "Create three 9:16 ad variants for my summer sale on this sneaker."
- "Find a Space in my workspace that makes product ad grids and tell me what a run costs."
- "Turn my latest product image into a short video clip."
- "Write a UGC storyboard for my face serum and make the shots."
- "Make a 30-second launch film for our app from PART 1.mp3 and our website."

## Support

- Documentation: https://sloosh.ai/docs/mcp
- Support: https://sloosh.ai/docs/support
- Privacy policy: https://sloosh.ai/privacy-policy
- Terms of use: https://sloosh.ai/terms-of-use
