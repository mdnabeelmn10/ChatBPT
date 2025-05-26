from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# import openai
from pymongo import MongoClient
import os
import google.generativeai as genai
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# from .utils.redis_utils import is_allowed,get_remaining_chats

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# openai.api_key = os.getenv("OPENAI_API_KEY")

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["chatbpt"]
collection = db["history"]

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat_with_gpt(request):
    user_input = request.data.get("message")
    user_id = str(request.user.id)
    username = request.user.username
    t = request.user.tier
    print(t)
    if t == "FREE":
        limit = 10
    else:
        limit = 1000


    try:
        # Step 1: Get start and end of today
        now = datetime.utcnow()
        start_of_day = datetime(now.year, now.month, now.day)
        end_of_day = start_of_day + timedelta(days=1)

        todays_chats = collection.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": start_of_day, "$lt": end_of_day}
        })

        if todays_chats >= limit:
            return Response({
                "reply": "You have reached the daily chat limit of 10. Please upgrade to continue chatting."
            }, status=429)


        if(t == "FREE"):
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(user_input)
            gpt_reply = response.text
        else:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(user_input)
            gpt_reply = response.text

        # Step 4: Save the chat with a timestamp
        collection.insert_one({
            "user_id": user_id,
            "username": username,
            "user_input": user_input,
            "bot_response": gpt_reply,
            "timestamp": now
        })
        print("Saved to DB:", {
        "user_id": str(request.user.id),
        "username": request.user.username,
        "query": user_input,
        "response": gpt_reply
    })

        return Response({
            "reply": gpt_reply,
            "username": username,
            "remchats": todays_chats + 1,
            "tier": t
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)

# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def chat_with_gpt(request):
#     user_input = request.data.get("message")
#     user_id = str(request.user.id)
#     username = request.user.username
#     t = request.user.tier
#     print(t)
#     if t == "FREE":
#         limit = 10
#     else:
#         limit = 1000


#     try:
#         # Step 1: Get start and end of today
#         now = datetime.utcnow()
#         start_of_day = datetime(now.year, now.month, now.day)
#         end_of_day = start_of_day + timedelta(days=1)

#         todays_chats = collection.count_documents({
#             "user_id": user_id,
#             "timestamp": {"$gte": start_of_day, "$lt": end_of_day}
#         })

#         if todays_chats >= limit:
#             return Response({
#                 "reply": "You have reached the daily chat limit of 10. Please upgrade to continue chatting."
#             }, status=429)


#         if(t == "FREE"):
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[{ "role": "user", "content": user_input }]
#             )
#             gpt_reply = response['choices'][0]['message']['content']
#         else:
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[{ "role": "user", "content": user_input }]
#             )
#             gpt_reply = response['choices'][0]['message']['content']

#         # Step 4: Save the chat with a timestamp
#         collection.insert_one({
#             "user_id": user_id,
#             "username": username,
#             "user_input": user_input,
#             "bot_response": gpt_reply,
#             "timestamp": now
#         })
#         print("Saved to DB:", {
#         "user_id": str(request.user.id),
#         "username": request.user.username,
#         "query": user_input,
#         "response": gpt_reply
#     })

#         return Response({
#             "reply": gpt_reply,
#             "username": username,
#             "remchats": todays_chats + 1,
#             "tier": t
#         })

#     except Exception as e:
#         return Response({"error": str(e)}, status=500)

# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def chat_with_gpt(request):
#     user_input = request.data.get("message")
#     user_id = str(request.user.id)
#     username = request.user.username

#     if not is_allowed(user_id, limit=10):  # set your desired limit
#         return Response({
#             "reply": "You have reached the daily chat limit of 10. Please upgrade to continue chatting."
#         }, status=429)

#     try:
#         model = genai.GenerativeModel('gemini-1.5-flash')
#         response = model.generate_content(user_input)
#         gpt_reply = response.text

#         collection.insert_one({
#             "user_id": user_id,
#             "username": username,
#             "user_input": user_input,
#             "bot_response": gpt_reply,
#             "timestamp": datetime.utcnow()
#         })

#         return Response({
#             "reply": gpt_reply,
#             "username": username,
#             "remchats": get_remaining_chats(user_id, limit=10)  
#         })

#     except Exception as e:
#         return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chat_history(request):
    user_id = str(request.user.id)
    history = list(collection.find({"user_id": user_id}))
    formatted_history = [{
        "user_input": entry.get("user_input", ""),
        "bot_response": entry.get("bot_response", ""),
        "username": entry.get("username", "")  
    } for entry in history]

    return Response({"history": formatted_history})


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def remaining_chats(request):
#     user_id = str(request.user.id)
#     remaining = get_remaining_chats(user_id, limit=10)
#     return Response({"remaining_chats": remaining})
