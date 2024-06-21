

PYTHON_BIN=/home/hatnote/virtualenvs/weeklypedia/bin/python
PUBLISH_SCRIPT=/home/hatnote/weeklypedia/weeklypedia/publish.py
LOG_BASE_PATH=/home/hatnote/weeklypedia/logs/cron_out

$PYTHON_BIN $PUBLISH_SCRIPT --lang en 2>&1 | tee -a $LOG_BASE_PATH/en.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang ko 2>&1 | tee -a $LOG_BASE_PATH/ko.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang de 2>&1 | tee -a $LOG_BASE_PATH/de.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang fr 2>&1 | tee -a $LOG_BASE_PATH/fr.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang et 2>&1 | tee -a $LOG_BASE_PATH/et.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang sv 2>&1 | tee -a $LOG_BASE_PATH/sv.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang da 2>&1 | tee -a $LOG_BASE_PATH/da.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang it 2>&1 | tee -a $LOG_BASE_PATH/it.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang ca 2>&1 | tee -a $LOG_BASE_PATH/ca.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang es 2>&1 | tee -a $LOG_BASE_PATH/es.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang fa 2>&1 | tee -a $LOG_BASE_PATH/fa.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang ur 2>&1 | tee -a $LOG_BASE_PATH/ur.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang kn 2>&1 | tee -a $LOG_BASE_PATH/kn.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang lv 2>&1 | tee -a $LOG_BASE_PATH/lv.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang el 2>&1 | tee -a $LOG_BASE_PATH/el.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang te 2>&1 | tee -a $LOG_BASE_PATH/te.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang oc 2>&1 | tee -a $LOG_BASE_PATH/oc.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang uk 2>&1 | tee -a $LOG_BASE_PATH/uk.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang ru 2>&1 | tee -a $LOG_BASE_PATH/ru.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang cs 2>&1 | tee -a $LOG_BASE_PATH/cs.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang eo 2>&1 | tee -a $LOG_BASE_PATH/eo.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang no 2>&1 | tee -a $LOG_BASE_PATH/no.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang nn 2>&1 | tee -a $LOG_BASE_PATH/nn.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang pt 2>&1 | tee -a $LOG_BASE_PATH/pt.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang zh 2>&1 | tee -a $LOG_BASE_PATH/zh.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang eu 2>&1 | tee -a $LOG_BASE_PATH/eu.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang tr 2>&1 | tee -a $LOG_BASE_PATH/tr.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang ar 2>&1 | tee -a $LOG_BASE_PATH/ar.txt
$PYTHON_BIN $PUBLISH_SCRIPT --lang nl 2>&1 | tee -a $LOG_BASE_PATH/nl.txt
