import time
import threading
from src.action_handler import register_action
from src.helpers import print_h_bar
from src.prompts import POST_BLUESKY_PROMPT, REPLY_BLUESKY_PROMPT


@register_action("post-bluesky")
def post_bluesky(agent, **kwargs):
    current_time = time.time()

    if "last_post_time" not in agent.state:
        last_post_time = 0
    else:
        last_post_time = agent.state["last_post_time"]

    post_interval = getattr(agent, "post_interval", 5400)
    if current_time - last_post_time >= post_interval:
        agent.logger.info("\n📝 GENERATING NEW BLUESKY POST")
        print_h_bar()

        prompt = POST_BLUESKY_PROMPT.format(agent_name=agent.name)
        post_text = agent.prompt_llm(prompt)

        if post_text:
            agent.logger.info("\n🚀 Posting bluesky post:")
            agent.logger.info(f"'{post_text}'")
            agent.connection_manager.perform_action(
                connection_name="bluesky",
                action_name="post-bluesky",
                params=[post_text]
            )
            agent.state["last_post_time"] = current_time
            agent.logger.info("\n✅ Bluesky post posted successfully!")
            return True
    else:
        agent.logger.info("\n👀 Delaying post until post interval elapses...")
        return False


# @register_action("reply-to-bluesky")
# def reply_to_bluesky(agent, **kwargs):
#     if "timeline_posts" in agent.state and agent.state["timeline_posts"] is not None and len(agent.state["timeline_posts"]) > 0:
#         post = agent.state["timeline_posts"].pop(0)
#         post_id = post.get('id')
#         if not post_id:
#             return

#         agent.logger.info(f"\n💬 GENERATING REPLY to: {post.get('text', '')[:50]}...")

#         base_prompt = REPLY_BLUESKY_PROMPT.format(post_text=post.get('text'))
#         system_prompt = agent._construct_system_prompt()
#         reply_text = agent.prompt_llm(prompt=base_prompt, system_prompt=system_prompt)

#         if reply_text:
#             agent.logger.info(f"\n🚀 Posting reply: '{reply_text}'")
#             agent.connection_manager.perform_action(
#                 connection_name="bluesky",
#                 action_name="reply-to-bluesky",
#                 params=[post_id, reply_text]
#             )
#             agent.logger.info("✅ Reply posted successfully!")
#             return True
#     else:
#         agent.logger.info("\n👀 No posts found to reply to...")
#         return False


# @register_action("like-bluesky")
# def like_bluesky(agent, **kwargs):
#     if "timeline_posts" in agent.state and agent.state["timeline_posts"] is not None and len(agent.state["timeline_posts"]) > 0:
#         post = agent.state["timeline_posts"].pop(0)
#         post_id = post.get('id')
#         if not post_id:
#             return False

#         is_own_post = post.get('author_username', '').lower() == agent.username
#         if is_own_post:
#             replies = agent.connection_manager.perform_action(
#                 connection_name="bluesky",
#                 action_name="get-post-replies",
#                 params=[post.get('author_id')]
#             )
#             if replies:
#                 agent.state["timeline_posts"].extend(replies[:agent.own_post_replies_count])
#             return True

#         agent.logger.info(f"\n👍 LIKING BLUESKY POST: {post.get('text', '')[:50]}...")

#         agent.connection_manager.perform_action(
#             connection_name="bluesky",
#             action_name="like-bluesky",
#             params=[post_id]
#         )
#         agent.logger.info("✅ Post liked successfully!")
#         return True
#     else:
#         agent.logger.info("\n👀 No posts found to like...")
#     return False


# @register_action("respond-to-bluesky-mentions")
# def respond_to_bluesky_mentions(agent, **kwargs):  # REQUIRES BLUESKY PREMIUM PLAN

#     filter_str = f"@{agent.username} -is:repost"
#     stream_function = agent.connection_manager.perform_action(
#         connection_name="bluesky",
#         action_name="stream-posts",
#         params=[filter_str]
#     )

#     def process_posts():
#         for post_data in stream_function:
#             post_id = post_data["id"]
#             post_text = post_data["text"]
#             agent.logger.info(f"Received a mention: {post_text}")

#     processing_thread = threading.Thread(target=process_posts)
#     processing_thread.daemon = True
#     processing_thread.start()