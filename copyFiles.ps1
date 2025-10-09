# Define the source paths
$sourceFile1 = "ai-hub-apps/tutorials/llm_on_genie/configs/htp/htp_backend_ext_config.json.template" 
$sourceFile2 = "ai-hub-apps/tutorials/llm_on_genie/configs/genie/phi_3_5_mini_instruct.json" 

# Define the local folder path
$localFolder = "genie_bundle"

 # Define the destination file paths using the local folder 
$destinationFile1 = Join-Path -Path $localFolder -ChildPath "htp_backend_ext_config.json" 
$destinationFile2 = Join-Path -Path $localFolder -ChildPath "genie_config.json" 

# Create the local folder if it doesn't exist 
if (-not (Test-Path -Path $localFolder)) {
    New-Item -ItemType Directory -Path $localFolder
}

# Copy the files to the local folder 
Copy-Item -Path $sourceFile1 -Destination $destinationFile1 -Force 
Copy-Item -Path $sourceFile2 -Destination $destinationFile2 -Force 
Write-Host "Files have been successfully copied to the genie_bundle folder with updated names."