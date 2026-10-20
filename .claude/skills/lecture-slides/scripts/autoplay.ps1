# 슬라이드에 들어 있는 모든 영상을 "슬라이드가 열리면 자동 재생"으로 설정한다.
# 사용: powershell -ExecutionPolicy Bypass -File autoplay.ps1 "<pptx 경로>"
param([string]$path)
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open($path, $false, $false, $false)
$n = 0
# 1) 재생 효과 만들기
foreach ($s in $p.Slides) {
    foreach ($sh in $s.Shapes) {
        if ($sh.Type -eq 16) {   # msoMedia
            $sh.AnimationSettings.PlaySettings.PlayOnEntry = -1
            $sh.AnimationSettings.PlaySettings.HideWhileNotPlaying = 0
            $n++
        }
    }
}
# 2) 클릭 없이 바로 재생되도록 영상 효과를 '이전 효과 다음에'(3)로
foreach ($s in $p.Slides) {
    $seq = $s.TimeLine.MainSequence
    for ($i = 1; $i -le $seq.Count; $i++) {
        $e = $seq.Item($i)
        if ($e.Shape.Type -eq 16) { $e.Timing.TriggerType = 3 }
    }
}
$p.Save()
$p.Close()
$app.Quit()
"autoplay set on $n videos"
