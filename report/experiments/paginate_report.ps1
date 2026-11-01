param(
    [string]$DocxPath='report/final/NhomXX_BombItMultiplayer_Report.docx',
    [string]$PdfPath='report/final/NhomXX_BombItMultiplayer_Report.pdf'
)
$ErrorActionPreference='Stop'
$reportRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$reportDocx=[IO.Path]::GetFullPath((Join-Path $reportRoot $DocxPath))
$reportPdf=[IO.Path]::GetFullPath((Join-Path $reportRoot $PdfPath))
$reportWord=$null;$reportDocument=$null
try{
    $reportWord=New-Object -ComObject Word.Application
    $reportWord.Visible=$false
    $reportWord.DisplayAlerts=0
    $reportWord.ScreenUpdating=$false
    $reportDocument=$reportWord.Documents.Open($reportDocx,$false,$false)
    foreach($reportStyleId in @(-20,-21,-22)){
        $reportStyle=$reportDocument.Styles.Item($reportStyleId)
        $reportStyle.Font.Name='Times New Roman';$reportStyle.Font.Size=11
        $reportStyle.ParagraphFormat.SpaceAfter=3
    }
    foreach($reportPass in 1..3){
        $reportDocument.Fields.Update() | Out-Null
        foreach($reportToc in $reportDocument.TablesOfContents){$reportToc.Update()}
        $reportDocument.Repaginate()
    }
    foreach($reportSection in $reportDocument.Sections){
        foreach($reportFooter in $reportSection.Footers){$reportFooter.Range.Fields.Update() | Out-Null}
    }
    $reportDocument.Save()
    $reportDocument.ExportAsFixedFormat($reportPdf,17)
    $reportPages=$reportDocument.ComputeStatistics(2)
    $reportChapterPages=@()
    foreach($reportParagraph in $reportDocument.Paragraphs){
        if($reportParagraph.OutlineLevel -eq 1 -and $reportParagraph.Range.Text -match '^([1-9]|1[0-9])\. '){
            $reportChapterPages+=@{title=$reportParagraph.Range.Text.Trim();page=$reportParagraph.Range.Information(3)}
        }
    }
    $reportTocTexts=@($reportDocument.TablesOfContents | ForEach-Object {$_.Range.Text})
    @{docx=$reportDocx;pdf=$reportPdf;pages=$reportPages;tables=$reportDocument.Tables.Count;inline_shapes=$reportDocument.InlineShapes.Count;toc_fields=$reportDocument.TablesOfContents.Count;toc_texts=$reportTocTexts;chapter_pages=$reportChapterPages;word_version=$reportWord.Version;updated_at=(Get-Date).ToString('o')} | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $reportRoot 'report/evidence/task18-2026-10-26/word-pagination.json')
    Write-Output "Word pagination complete: pages=$reportPages TOCs=$($reportDocument.TablesOfContents.Count) tables=$($reportDocument.Tables.Count) images=$($reportDocument.InlineShapes.Count)"
}finally{
    if($null -ne $reportDocument){$reportDocument.Close(0)}
    if($null -ne $reportWord){$reportWord.Quit();[Runtime.InteropServices.Marshal]::FinalReleaseComObject($reportWord) | Out-Null}
    [GC]::Collect();[GC]::WaitForPendingFinalizers()
}
