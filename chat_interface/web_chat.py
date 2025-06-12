from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import requests # اگر برای ارسال درخواست به API داخلی استفاده کنی، میتونی اینو نگه داری، در غیر این صورت حذفش کن

router = APIRouter()

@router.get("/ui", response_class=HTMLResponse)
async def chat_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>AI Call Center Chat</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://netdna.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
        <style type="text/css">
            * {
                box-sizing: border-box;
            }

            body {
                background-color: #edeff2;
                font-family: "Calibri", "Roboto", sans-serif;
            }

            .chat_window {
                position: absolute;
                width: calc(100% - 20px);
                max-width: 800px;
                height: 500px;
                border-radius: 10px;
                background-color: #fff;
                left: 50%;
                top: 50%;
                transform: translateX(-50%) translateY(-50%);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
                background-color: #f8f8f8;
                overflow: hidden;
            }

            .top_menu {
                background-color: #fff;
                width: 100%;
                padding: 20px 0 15px;
                box-shadow: 0 1px 30px rgba(0, 0, 0, 0.1);
            }
            .top_menu .buttons {
                margin: 3px 0 0 20px;
                position: absolute;
            }
            .top_menu .buttons .button {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 10px;
                position: relative;
            }
            .top_menu .buttons .button.close {
                background-color: #f5886e;
            }
            .top_menu .buttons .button.minimize {
                background-color: #fdbf68;
            }
            .top_menu .buttons .button.maximize {
                background-color: #a3d063;
            }
            .top_menu .title {
                text-align: center;
                color: #bcbdc0;
                font-size: 20px;
            }

            .messages {
                position: relative;
                list-style: none;
                padding: 20px 10px 0 10px;
                margin: 0;
                height: 347px;
                overflow: scroll;
            }
            .messages .message {
                clear: both;
                overflow: hidden;
                margin-bottom: 20px;
                transition: all 0.5s linear;
                opacity: 0;
            }
            .messages .message.left .avatar {
                background-color: #f5886e;
                float: left;
            }
            .messages .message.left .text_wrapper {
                background-color: #ffe6cb;
                margin-left: 20px;
            }
            .messages .message.left .text_wrapper::after, .messages .message.left .text_wrapper::before {
                right: 100%;
                border-right-color: #ffe6cb;
            }
            .messages .message.left .text {
                color: #c48843;
            }
            .messages .message.right .avatar {
                background-color: #fdbf68;
                float: right;
            }
            .messages .message.right .text_wrapper {
                background-color: #c7eafc;
                margin-right: 20px;
                float: right;
            }
            .messages .message.right .text_wrapper::after, .messages .message.right .text_wrapper::before {
                left: 100%;
                border-left-color: #c7eafc;
            }
            .messages .message.right .text {
                color: #45829b;
            }
            .messages .message.appeared {
                opacity: 1;
            }
            .messages .message .avatar {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                display: inline-block;
            }
            .messages .message .text_wrapper {
                display: inline-block;
                padding: 20px;
                border-radius: 6px;
                width: calc(100% - 85px);
                min-width: 100px;
                position: relative;
            }
            .messages .message .text_wrapper::after, .messages .message .text_wrapper:before {
                top: 18px;
                border: solid transparent;
                content: " ";
                height: 0;
                width: 0;
                position: absolute;
                pointer-events: none;
            }
            .messages .message .text_wrapper::after {
                border-width: 13px;
                margin-top: 0px;
            }
            .messages .message .text_wrapper::before {
                border-width: 15px;
                margin-top: -2px;
            }
            .messages .message .text_wrapper .text {
                font-size: 18px;
                font-weight: 300;
            }

            .bottom_wrapper {
                position: relative;
                width: 100%;
                background-color: #fff;
                padding: 20px 20px;
                position: absolute;
                bottom: 0;
            }
            .bottom_wrapper .message_input_wrapper {
                display: inline-block;
                height: 50px;
                border-radius: 25px;
                border: 1px solid #bcbdc0;
                width: calc(100% - 160px);
                position: relative;
                padding: 0 20px;
            }
            .bottom_wrapper .message_input_wrapper .message_input {
                border: none;
                height: 100%;
                box-sizing: border-box;
                width: calc(100% - 40px);
                position: absolute;
                outline-width: 0;
                color: gray;
            }
            .bottom_wrapper .send_message {
                width: 140px;
                height: 50px;
                display: inline-block;
                border-radius: 50px;
                background-color: #a3d063;
                border: 2px solid #a3d063;
                color: #fff;
                cursor: pointer;
                transition: all 0.2s linear;
                text-align: center;
                float: right;
            }
            .bottom_wrapper .send_message:hover {
                color: #a3d063;
                background-color: #fff;
            }
            .bottom_wrapper .send_message .text {
                font-size: 18px;
                font-weight: 300;
                display: inline-block;
                line-height: 48px;
            }

            .message_template {
                display: none;
            }
        </style>
    </head>
    <body>
    <div class="chat_window">
        <div class="top_menu">
            <div class="buttons">
                <div class="button close"></div>
                <div class="button minimize"></div>
                <div class="button maximize"></div>
            </div>
            <div class="title">AI Assistant Chat</div>
        </div>
        <ul class="messages"></ul>
        <div class="bottom_wrapper clearfix">
            <div class="message_input_wrapper">
                <input class="message_input" placeholder="Type your message here..." />
            </div>
            <div class="send_message">
                <div class="icon"></div>
                <div class="text">Send</div>
            </div>
        </div>
    </div>
    <div class="message_template">
        <li class="message">
            <div class="avatar"></div>
            <div class="text_wrapper">
                <div class="text"></div>
            </div>
        </li>
    </div>
    <script src="https://code.jquery.com/jquery-1.10.2.min.js"></script>
    <script src="https://netdna.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <script type="text/javascript">
        (function () {
            var Message;
            Message = function (arg) {
                this.text = arg.text, this.message_side = arg.message_side;
                this.draw = function (_this) {
                    return function () {
                        var $message;
                        $message = $($('.message_template').clone().html());
                        $message.addClass(_this.message_side).find('.text').html(_this.text);
                        $('.messages').append($message);
                        return setTimeout(function () {
                            return $message.addClass('appeared');
                        }, 0);
                    };
                }(this);
                return this;
            };

            // This function will handle sending messages to your FastAPI backend
            async function sendMessageToAPI(messageText) {
                try {
                    const response = await fetch("/chat", { // Make sure this path is correct based on your main.py routing
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ text: messageText, source: "chat", lang: "en" })
                    });
                    const data = await response.json();
                    return data.reply; // Assuming your FastAPI endpoint returns {"reply": "..."}
                } catch (error) {
                    console.error("Error sending message to API:", error);
                    return "Sorry, something went wrong."; // Handle API errors gracefully
                }
            }

            $(function () {
                var getMessageText, message_side, sendMessage;
                message_side = 'right'; // Start with user messages on the right

                getMessageText = function () {
                    var $message_input;
                    $message_input = $('.message_input');
                    return $message_input.val();
                };

                sendMessage = async function (text, sender_is_user = true) { // Added sender_is_user parameter
                    var $messages, message;
                    if (text.trim() === '') {
                        return;
                    }
                    $('.message_input').val('');
                    $messages = $('.messages');

                    // Determine message side based on who is sending it
                    const current_message_side = sender_is_user ? 'right' : 'left';

                    message = new Message({
                        text: text,
                        message_side: current_message_side
                    });
                    message.draw();
                    $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 300);

                    // If the sender is the user, send to API and then display bot's reply
                    if (sender_is_user) {
                        const botReply = await sendMessageToAPI(text);
                        sendMessage(botReply, false); // Display bot's reply
                    }
                };

                // Event listener for "Send" button click
                $('.send_message').click(function (e) {
                    return sendMessage(getMessageText(), true); // User sends message
                });

                // Event listener for Enter key press in input field
                $('.message_input').keyup(function (e) {
                    if (e.which === 13) {
                        return sendMessage(getMessageText(), true); // User sends message
                    }
                });

                // Initial welcome message from the bot
                setTimeout(function () {
                    return sendMessage('Hello! How can I help you today?', false); // Bot sends initial message
                }, 500); // A small delay to make it appear natural

            });
        }.call(this));
    </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)