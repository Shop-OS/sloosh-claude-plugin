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

## Use the skills in other agents

Each skill is a folder with a SKILL.md file in the open Agent Skills format. Other coding agents can install some or all of the skills. The skills call the Sloosh tools. First connect the Sloosh server in that agent, then install the skills. In Claude Code, use the plugin. Do not also copy the skills into `~/.claude/skills`.

### Connect the Sloosh server

Add the Sloosh server with this URL: https://mcp.sloosh.ai/mcp. Then sign in to Sloosh and authorize your workspace.

- Codex: run `codex mcp add sloosh --url https://mcp.sloosh.ai/mcp`. Codex opens the Sloosh sign-in. If it does not, run `codex mcp login sloosh`.
- Cursor: add `{"mcpServers":{"sloosh":{"url":"https://mcp.sloosh.ai/mcp"}}}` to `~/.cursor/mcp.json`.
- Gemini CLI: run `gemini mcp add --transport http -s user sloosh https://mcp.sloosh.ai/mcp`. Start Gemini CLI in a folder that you trust, then run `/mcp auth sloosh`.
- Muse Code: add `"sloosh":{"transport":"streamable_http","url":"https://mcp.sloosh.ai/mcp","enabled":true,"mode":"optional"}` to the `mcp_servers` block in `~/.config/muse/settings.json`. A new file must also set `"schema_version": 1`. Then run `muse mcp login sloosh`.

### Install skills with the skills CLI

List the skills in this repository:

```
npx skills@1.7.2 add Shop-OS/sloosh-claude-plugin --list
```

Install the skills you want for the agents you name. With `-g`, the CLI puts one copy in `~/.agents/skills`, which Codex, Cursor and Gemini CLI all read:

```
npx skills@1.7.2 add Shop-OS/sloosh-claude-plugin --skill product-imagery product-video -a codex cursor gemini-cli -g -y
```

Always name the agents with `-a`. Without it, the CLI installs the skills into every agent it supports, Claude Code included. The skills CLI is a third-party tool. It sends this repository's name and the skill names to skills.sh. Set `DISABLE_TELEMETRY=1` to stop this.

Some skills hand work to other skills. Install them together:

- `product-video`, `ad-variants`, `ugc-storyboard` and `launch-film` use `product-imagery`.
- `ugc-storyboard` and `launch-film` use `product-video`.
- `ad-variants` and `ugc-storyboard` can use `published-spaces`.
- `launch-film` needs its whole folder, with `scripts/`, `assets/` and `references/`. See the Launch films section below for what it needs on your computer.

### Install the plugin in Codex

Codex can install the whole plugin from this repository, with the six skills and the Sloosh server:

```
codex plugin marketplace add Shop-OS/sloosh-claude-plugin
codex plugin add sloosh@sloosh
codex mcp login sloosh
```

## Launch films

The launch film skill directs and renders a SaaS or product launch film with Remotion on your computer, cut to your voiceover. It runs in a coding agent that can run commands on your computer, such as Claude Code. It needs Node.js, ffmpeg, and Python 3 with numpy and Pillow. It transcribes the voiceover with whisper-cpp and a speech model. The agent asks you before it installs either. It can use Sloosh images and clips for missing shots after you approve each quote. Remotion is free for individuals, non-profits and for-profit companies with up to three employees. Larger for-profit companies need a Remotion company license.

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
