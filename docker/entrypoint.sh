#!/bin/bash
set -e

# build prefix
ALFR3D_PREFIX=${ALFR3D_PREFIX:-""}
# path to config.json
ALFR3D_CONFIG_PATH=${ALFR3D_CONFIG_PATH:-""}
# execution command line
ALFR3D_EXEC=${ALFR3D_EXEC:-""}

# use environment variables to pass parameters
# if you have not defined environment variables, set them below
# export OPEN_AI_API_KEY=${OPEN_AI_API_KEY:-'YOUR API KEY'}
# export OPEN_AI_PROXY=${OPEN_AI_PROXY:-""}
# export SINGLE_CHAT_PREFIX=${SINGLE_CHAT_PREFIX:-'["bot", "@bot"]'}
# export SINGLE_CHAT_REPLY_PREFIX=${SINGLE_CHAT_REPLY_PREFIX:-'"[bot] "'}
# export GROUP_CHAT_PREFIX=${GROUP_CHAT_PREFIX:-'["@bot"]'}
# export GROUP_NAME_WHITE_LIST=${GROUP_NAME_WHITE_LIST:-'["ChatGPT测试群", "ChatGPT测试群2"]'}
# export IMAGE_CREATE_PREFIX=${IMAGE_CREATE_PREFIX:-'["画", "看", "找"]'}
# export CONVERSATION_MAX_TOKENS=${CONVERSATION_MAX_TOKENS:-"1000"}
# export SPEECH_RECOGNITION=${SPEECH_RECOGNITION:-"False"}
# export CHARACTER_DESC=${CHARACTER_DESC:-"你是ChatGPT, 一个由OpenAI训练的大型语言模型, 你旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。"}
# export EXPIRES_IN_SECONDS=${EXPIRES_IN_SECONDS:-"3600"}

# ALFR3D_PREFIX is empty, use /app
if [ "$ALFR3D_PREFIX" == "" ] ; then
    ALFR3D_PREFIX=/app
fi

# ALFR3D_CONFIG_PATH is empty, use '/app/config.json'
if [ "$ALFR3D_CONFIG_PATH" == "" ] ; then
    ALFR3D_CONFIG_PATH=$ALFR3D_PREFIX/config.json
fi

# ALFR3D_EXEC is empty, use ‘python app.py’
if [ "$ALFR3D_EXEC" == "" ] ; then
    ALFR3D_EXEC="python app.py"
fi

# modify content in config.json
# if [ "$OPEN_AI_API_KEY" == "YOUR API KEY" ] || [ "$OPEN_AI_API_KEY" == "" ]; then
#     echo -e "\033[31m[Warning] You need to set OPEN_AI_API_KEY before running!\033[0m"
# fi


# fix ownership of mounted volumes then drop to non-root user
if [ "$(id -u)" = "0" ]; then
    mkdir -p /home/agent/alfr3d
    chown agent:agent /home/agent/alfr3d
    exec su agent -s /bin/bash -c "cd $ALFR3D_PREFIX && $ALFR3D_EXEC"
fi

# fallback: already running as agent
cd $ALFR3D_PREFIX
$ALFR3D_EXEC


