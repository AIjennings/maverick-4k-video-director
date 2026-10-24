# ==============================================================================
# MAVERICK 4K Video Director + Eden Mazara 4K Commercial — DomAI 1-Click Setup
# ==============================================================================
# Run in PowerShell on DomAI:
#   irm https://raw.githubusercontent.com/AIjennings/maverick-4k-video-director/main/setup-domai.ps1 | iex
# ==============================================================================

param(
    [switch]$IncludeMasterRenders = $false,
    [switch]$NoPreview = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n==============================================================================" -ForegroundColor Cyan
Write-Host "  MAVERICK 4K VIDEO DIRECTOR + EDEN MAZARA 4K COMMERCIAL — DOMAI INSTALLER" -ForegroundColor Cyan
Write-Host "==============================================================================`n" -ForegroundColor Cyan

# 1. Select Base Workspace Directory (D:\AI if D: drive exists, else C:\AI)
$DriveRoot = if (Test-Path "D:\") { "D:\AI" } else { "C:\AI" }
$WorkRoot = Join-Path $DriveRoot "HyperFramesVideos"
$RepoDir = Join-Path $WorkRoot "maverick-4k-video-director"
$ProjDir = Join-Path $WorkRoot "eden-mazara-commercial"

New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null
New-Item -ItemType Directory -Force -Path $ProjDir | Out-Null

Write-Host "[1/5] Syncing MAVERICK 4K Video Director repository to $RepoDir ..." -ForegroundColor Yellow
if (Test-Path (Join-Path $RepoDir ".git")) {
    git -C $RepoDir pull origin main
} else {
    git clone https://github.com/AIjennings/maverick-4k-video-director.git $RepoDir
}

# 2. Install Maverick & Flow CLI Skills into Antigravity IDE, Hermes, and Claude
Write-Host "`n[2/5] Installing maverick-video-director & flow-cli agent skills ..." -ForegroundColor Yellow
$SkillTargets = @(
    (Join-Path $HOME ".gemini\config\skills"),
    (Join-Path $HOME ".hermes\skills"),
    (Join-Path $env:LOCALAPPDATA "hermes\skills"),
    (Join-Path $HOME ".claude\skills")
)

foreach ($TargetRoot in $SkillTargets) {
    New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null
    foreach ($SkillName in @("maverick-video-director", "flow-cli")) {
        $SrcSkill = Join-Path $RepoDir "skills\$SkillName"
        $DstSkill = Join-Path $TargetRoot $SkillName
        if (Test-Path $SrcSkill) {
            New-Item -ItemType Directory -Force -Path $DstSkill | Out-Null
            Copy-Item -Path (Join-Path $SrcSkill "*") -Destination $DstSkill -Recurse -Force
            Write-Host "  + Installed $SkillName -> $DstSkill" -ForegroundColor Green
        }
    }
}

# 3. Download & Extract the Complete Eden Mazara 4K Project Workspace (1.01 GB)
$WorkspaceZipId = "1Rf5iakdFyCTnT-PR2mbHoFyH4B_GobnJ"
$WorkspaceZipPath = Join-Path $WorkRoot "Eden-Mazara-4K-Project-Workspace.zip"
$MarkerAsset = Join-Path $ProjDir "assets\website\dji_eden_mazara_ridge_to_bay_finale.jpg"

if (-not (Test-Path $MarkerAsset)) {
    Write-Host "`n[3/5] Downloading Eden-Mazara-4K-Project-Workspace.zip (1.01 GB, 144 4K/30fps assets) ..." -ForegroundColor Yellow
    $DownloadUrl = "https://drive.usercontent.google.com/download?id=$WorkspaceZipId&export=download&confirm=t"
    & curl.exe -L --fail --progress-bar -o $WorkspaceZipPath $DownloadUrl
    Write-Host "  + Extracting workspace into $ProjDir ..." -ForegroundColor Yellow
    & tar.exe -xf $WorkspaceZipPath -C $ProjDir
    Write-Host "  + Workspace extracted successfully!" -ForegroundColor Green
} else {
    Write-Host "`n[3/5] Eden Mazara 4K assets already present at $ProjDir — syncing latest compositions..." -ForegroundColor Green
    Copy-Item -Path (Join-Path $RepoDir "eden-mazara-v10-blueprint\*") -Destination $ProjDir -Recurse -Force
}

# Optional: Download rendered 4K UHD MP4s into renders/
if ($IncludeMasterRenders) {
    $RendersDir = Join-Path $ProjDir "renders"
    New-Item -ItemType Directory -Force -Path $RendersDir | Out-Null
    $Renders = @(
        @{ Id = "1N3_NPqQS4Ll31fWP7Xjh6XhJGssXBkX9"; Name = "Eden-Mazara-4K-Website-Showcase-Sizzle-20s-3840x2160.mp4" },
        @{ Id = "1dzH22bgV4Jd5uipNJ70QPFpX8Kq3vPDL"; Name = "MAVERICK-4K-LinkedIn-Sizzle-Reel-45s-3840x2160.mp4" },
        @{ Id = "1X3-w8n1nWvwkb1X-x3HxeLkmlsQAAIfx"; Name = "Eden-Mazara-4K-Full-Commercial-Master-150s-3840x2160.mp4" }
    )
    foreach ($Item in $Renders) {
        $OutMp4 = Join-Path $RendersDir $Item.Name
        if (-not (Test-Path $OutMp4)) {
            Write-Host "  + Downloading $($Item.Name) ..." -ForegroundColor Yellow
            & curl.exe -L --fail --progress-bar -o $OutMp4 "https://drive.usercontent.google.com/download?id=$($Item.Id)&export=download&confirm=t"
        }
    }
}

# 4. Install Node Dependencies & Verify HyperFrames Project
Write-Host "`n[4/5] Installing Node dependencies in $ProjDir ..." -ForegroundColor Yellow
Push-Location $ProjDir
try {
    npm install
} finally {
    Pop-Location
}

Write-Host "`n==============================================================================" -ForegroundColor Green
Write-Host "  READY ON DOMAI!" -ForegroundColor Green
Write-Host "  Project Workspace : $ProjDir" -ForegroundColor White
Write-Host "  Maverick CLI      : python `"$RepoDir\cli\maverick.py`" status --project `"$ProjDir`"" -ForegroundColor White
Write-Host "  4K UHD Render     : python `"$ProjDir\production\normalize_keyframes_and_render_4k.py`"" -ForegroundColor White
Write-Host "  4K Sizzle Reels   : python `"$ProjDir\production\rerender_derivatives_4k.py`"" -ForegroundColor White
Write-Host "  Google Drive Vault: https://drive.google.com/drive/folders/1tlwUsgeHmwO2vzP-wl5i8wA88kOtnuhJ" -ForegroundColor White
Write-Host "==============================================================================`n" -ForegroundColor Green

# 5. Launch Live HyperFrames Studio Preview
if (-not $NoPreview) {
    Write-Host "[5/5] Launching HyperFrames Studio Preview in $ProjDir ..." -ForegroundColor Cyan
    Set-Location $ProjDir
    npx hyperframes preview
}
