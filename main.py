import uuid
from asyncio import Semaphore

import uvicorn
from fastapi import BackgroundTasks
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from report import generate_report, report_id_valid, fetch_report

if __name__ == '__main__':

    app = FastAPI()

    # Data model for response payloads
    class TriggerReportResponse(BaseModel):
        report_id: str


    # Semaphore to limit the number of concurrent report generations
    MAX_CONCURRENT_REPORTS = 2
    report_generation_semaphore = Semaphore(MAX_CONCURRENT_REPORTS)


    @app.post("/trigger_report", response_model=TriggerReportResponse)
    async def trigger_report(background_tasks: BackgroundTasks):
        # Generate a random report_id
        report_id = str(uuid.uuid4())

        # Check if Semaphore has available slots
        if report_generation_semaphore.locked():
            # Return an error response indicating that the maximum number of reports are being generated
            return JSONResponse(content={"error": "Too many reports are being generated. Please try again later."},
                                status_code=503)

        # Acquire the Semaphore to limit the number of concurrent report generations
        await report_generation_semaphore.acquire()

        # Queue a background task to generate the report asynchronously
        background_tasks.add_task(generate_report, report_id, report_generation_semaphore)

        return JSONResponse(content={"report_id": report_id}, status_code=200)


    @app.get("/get_report/{report_id}")
    async def get_report(report_id: str):
        if report_id_valid(report_id):
            report = fetch_report(report_id)
            if report is None:
                return JSONResponse(content={"status": "Running"}, status_code=200)
            else:
                return FileResponse(report, filename=f"report.csv", media_type="text/csv")
        else:
            return JSONResponse(content={"error": "Invalid report id"}, status_code=400)

    uvicorn.run(app, host="0.0.0.0")
