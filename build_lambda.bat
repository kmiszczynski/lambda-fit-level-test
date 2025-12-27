@echo off
echo Building Lambda deployment package...

REM Clean up any existing build artifacts
if exist lambda_function.zip del lambda_function.zip
if exist package rmdir /s /q package

REM Create package directory
mkdir package

REM Copy only the required Python files (boto3 is already in AWS Lambda runtime)
copy lambda_handler.py package\
copy db_service.py package\
copy validator.py package\
copy level_calculator.py package\

REM Create ZIP file
cd package
powershell -Command "Compress-Archive -Path * -DestinationPath ..\lambda_function.zip -Force"
cd ..

REM Clean up
rmdir /s /q package

echo.
echo Lambda package created: lambda_function.zip
echo Package contains only the required Python files.
echo boto3 is already available in AWS Lambda runtime.