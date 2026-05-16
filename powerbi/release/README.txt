PBIX binaries are intentionally omitted from Git (large binary churn).

Produce CoreSpacesRenewal.pbix:

1. Install current Power BI Desktop (supports PBIR / PBIP authoring).
2. Open CoreSpacesRenewal.pbip beside this folder using File > Open > Browse Reports.
3. Refresh the semantic model after regenerating ..\..\data\gold\gold_renewal_scores.csv (run scripts/run_local_pipeline.py).
4. File > Save As and choose *.pbix for reviewers who prefer a single portable file.

TMDL note (semantic model authoring):
In model.tmdl, lines like "ref table ..." and "ref cultureInfo ..." must begin at column 0 with no leading tab or spaces.
Only properties inside the model block use tab indentation; mis-indenting refs triggers InvalidLineType / ReferenceObject parse errors in Desktop.
In table *.tmdl files, each column must use a separate line for dataType (e.g. "column lease_id" then tab-indented "dataType: string"); putting dataType on the same line as the column name causes Invalid indentation errors.
Do not hand-edit cultures/en-US.tmdl linguisticMetadata as JSON unless Power BI emits it — Desktop may validate linguistic metadata as XML; a malformed blob causes Xml content-type / DataModelLoadFailed on open.
