import os
import json
import uuid
import asyncio
import traceback
import nodes
import comfy.model_management

from aiohttp import web

import execution
import folder_paths

# =========================
# CONFIG
# =========================
WORKFLOW_PATH = "E:/__workspace/images2video_4_tool/ComfyUI/workflows/Main_test_current.json"
NODE_ID = "18"
HOST = "0.0.0.0"
PORT = 8188


# =========================
# SERVER
# =========================
class ComfyUIServer:

    def __init__(self):
        self.app = web.Application()
        self.routes = web.RouteTableDef()
        self.prompt_queue = execution.PromptQueue(self)

        self.register_routes()
        self.app.add_routes(self.routes)

    def register_routes(self):

        @self.routes.get("/")
        async def home(request):
            return web.json_response({
                "status": "ComfyUI API running",
                "endpoint": "/api/run-image"
            })

        # =========================
        # MAIN API
        # =========================
        @self.routes.post("/api/run-image")
        async def run_image(request):
            try:
                # =========================
                # 1. RECEIVE FILE
                # =========================
                reader = await request.multipart()
                field = await reader.next()

                if field is None or field.name != "file":
                    return web.json_response({"error": "file field required"}, status=400)

                filename = field.filename or f"{uuid.uuid4().hex}.jpg"

                input_dir = folder_paths.get_input_directory()
                save_path = os.path.join(input_dir, filename)

                with open(save_path, "wb") as f:
                    while True:
                        chunk = await field.read_chunk()
                        if not chunk:
                            break
                        f.write(chunk)

                print(f"[INFO] Saved file: {save_path}")

                # =========================
                # 2. LOAD WORKFLOW (API FORMAT)
                # =========================
                if not os.path.exists(WORKFLOW_PATH):
                    return web.json_response({"error": "workflow not found"}, status=500)

                with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
                    workflow = json.load(f)

                # DEBUG
                print("[DEBUG] Workflow keys:", list(workflow.keys())[:5])

                # =========================
                # 3. INJECT IMAGE NODE 18
                # =========================
                if NODE_ID not in workflow:
                    return web.json_response({
                        "error": f"Node {NODE_ID} not found"
                    }, status=400)

                workflow[NODE_ID]["inputs"]["image"] = filename

                print(f"[INFO] Injected image into node {NODE_ID}")

                # =========================
                # 4. VALIDATE
                # =========================
                prompt_id = str(uuid.uuid4())

                valid = await execution.validate_prompt(prompt_id, workflow, None)

                if not valid[0]:
                    return web.json_response({
                        "error": "invalid workflow",
                        "details": valid[1]
                    }, status=400)

                # =========================
                # 5. RUN
                # =========================
                self.prompt_queue.put((
                    0,
                    prompt_id,
                    workflow,
                    {},
                    valid[2],
                    {}
                ))

                print(f"[INFO] Running prompt: {prompt_id}")

                # =========================
                # 6. WAIT RESULT
                # =========================
                while True:
                    history = self.prompt_queue.get_history(prompt_id=prompt_id)

                    if prompt_id in history:
                        result = history[prompt_id]

                        outputs = result.get("outputs", {})

                        # =========================
                        # 7. RETURN MP4 FILE
                        # =========================
                        for node_outputs in outputs.values():
                            for item in node_outputs:
                                if "filename" in item:
                                    output_file = item["filename"]
                                    output_dir = folder_paths.get_output_directory()
                                    file_path = os.path.join(output_dir, output_file)

                                    if os.path.exists(file_path):
                                        print(f"[INFO] Returning file: {file_path}")

                                        return web.FileResponse(
                                            file_path,
                                            headers={
                                                "Content-Disposition": f"attachment; filename={output_file}"
                                            }
                                        )

                        # fallback
                        return web.json_response(result)

                    await asyncio.sleep(1)

            except Exception as e:
                return web.json_response({
                    "error": str(e),
                    "trace": traceback.format_exc()
                }, status=500)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    server = ComfyUIServer()

    print("\n🚀 Server running at:")
    print(f"👉 http://127.0.0.1:{PORT}")
    print(f"👉 http://<YOUR_IP>:{PORT}")
    print(f"👉 API: http://<YOUR_IP>:{PORT}/api/run-image\n")

    web.run_app(server.app, host=HOST, port=PORT)