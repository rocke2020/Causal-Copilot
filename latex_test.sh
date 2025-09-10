root_dir=output/Abalone.csv/20250910_102723/output_report
out_dir=$root_dir/out
tex_file=$root_dir/report.tex
log_file=$out_dir/latex_test.log
mkdir -p $out_dir
latexmk -bibtex -interaction=nonstopmode -halt-on-error -pdfxe -f -outdir=$out_dir \
    $tex_file 2>&1 | tee $log_file
