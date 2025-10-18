# GitHub - krazyness/CRBot-public

**URL:** https://github.com/krazyness/CRBot-public

---

Skip to content
Navigation Menu
Platform
Solutions
Resources
Open Source
Enterprise
Pricing
Sign in
Sign up
krazyness
/
CRBot-public
Public
Notifications
Fork 47
 Star 238
Code
Issues
8
Pull requests
2
Actions
Projects
Security
Insights
krazyness/CRBot-public
 main
1 Branch
0 Tags
Code
Folders and files
Name	Last commit message	Last commit date

Latest commit
krazyness
Fix roboflow links on README
d5579c3
 · 
History
16 Commits


__pycache__
	
Add initial model metadata and requirements file
	


main_images
	
Import into public repository
	


models
	
Add initial model metadata and requirements file
	


screenshots
	
Add initial model metadata and requirements file
	


.env.example
	
add .env support for the workspaces
	


.gitignore
	
feat: Add .env support
	


Actions.py
	
Import into public repository
	


LICENSE
	
Initial commit
	


README.md
	
Fix roboflow links on README
	


dqn_agent.py
	
Import into public repository
	


elixir_verification.py
	
Import into public repository
	


env.py
	
fix(reward): use only y positions for enemy presence to prevent right…
	


requirements.txt
	
feat: Add .env support
	


test_cards.py
	
Import into public repository
	


train.py
	
Import into public repository
	
Repository files navigation
README
MIT license
Clash Royale Bot

Bot that plays Clash Royale and learns by playing games
Explore the docs »
Report Bug · Request Feature

Table of Contents
About The Project

A Python-based Clash Royale AI bot that learns and improves through gameplay. This project aims to help others understand machine learning, reinforcement learning, and game automation in a practical context.

(Disclaimer: This project is not affiliated with Supercell. Use at your own risk—automated gameplay may violate Clash Royale's Terms of Service.)

(back to top)

Built With

(back to top)

Getting Started
Prerequisites
Windows (since that's the only OS it works on right now)
VSCode (unless you're more familiar with other code editors)
Docker
Roboflow Account
BlueStacks
Python 3.12
inference_sdk
pip install inference-sdk

PyTorch
pip install torch

PyAutoGUI
pip install PyAutoGUI

NumPy
pip install numpy

Installation
Create a Roboflow account as well as a workspace, then get your API key 
Clone the repo
git clone https://github.com/krazyness/CRBot-public.git
Set up your environment variables:
Copy .env.example to .env
Edit .env and replace your_roboflow_api_key_here with your actual Roboflow private API key
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
ROBOFLOW_API_KEY=your_actual_api_key_here
Fork both workflows: Troop Detection Card Detection

Get the workspace names from your forked workflows and update your .env file:

For the Troop Detection workspace, update WORKSPACE_TROOP_DETECTION=your-troop-workspace-name
For the Card Detection workspace, update WORKSPACE_CARD_DETECTION=your-card-workspace-name

Your .env file should look like:

ROBOFLOW_API_KEY=your_actual_api_key_here
WORKSPACE_TROOP_DETECTION=workspace-your-troop-name
WORKSPACE_CARD_DETECTION=workspace-your-card-name

Open Docker, and open the terminal on the bottom right, and install inference-cli (don't worry the terminal isn't stuck, it takes a long time)

pip install inference-cli

Start the Inference Server

inference server start

Open http://localhost:9001/, and it should take you to the Roboflow Inference page.

Open BlueStacks, and open the "multi-instance manager" (should be the third icon above the Discord icon, or its in the 3 dots), and create a fresh Pie 64-bit instance.

Start the Pie 64-bit instance, open Google Play Store, and install Clash Royale.

Optional: remove the ads on the left by opening settings (gear), > Preferences > Allow BlueStacks to show Ads during gameplay (disabled)

Open Clash Royale, resize and position the window like so (stretched and to the right-most of the screen)

Log in (or make a new) account on Clash Royale, click on battle, then run train.py, but immediately after, make sure the BlueStacks emulator is the front-most window.

NOTE: The bot is broken right now, with it not handling "play again" correctly, as well as some minor bugs in gameplay. You can ask me any questions at the contacts page, or make contributions at the contributing page!

(back to top)

Usage

(back to top)

Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request

(back to top)

License

Distributed under the project_license. See LICENSE.txt for more information.

(back to top)

Contact

Brody Dai - itrytomakestuff99@gmail.com

Project Link: https://github.com/krazyness/CRBot-public

(back to top)

Acknowledgments
Best README Template
Mr. Foster, AP Computer Science teacher

(back to top)

About
No description, website, or topics provided.
Resources
 Readme
License
 MIT license
 Activity
Stars
 238 stars
Watchers
 5 watching
Forks
 47 forks
Report repository


Releases
No releases published


Packages
No packages published



Contributors
3
krazyness Brody Dai
Soif2Sang Max
DakshSahni4


Languages
Python
100.0%
Footer
© 2025 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Community
Docs
Contact
Manage cookies
Do not share my personal information