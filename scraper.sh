export CLIENT_ID=
export SECRET_ID=
export REDDIT_USERNAME=
export REDDIT_PASSWORD=
export REDDIT_USER_AGENT=
export DB_NAME=
export TABLE_NAME=
export DB_USER=
export DB_PASSWORD=

recurse=false
debug=false

while getopts ":rd" option; do
    case $option in
        r) recurse=true ;;
        d) debug=true ;;
        ?) echo "usage: $0 [-r] [-d]"; exit ;;
    esac
done

shift $(( OPTIND - 1))
ls_opts=()
$recurse && ls_opts+=( -r )
$debug && ls_opts+=( -d )

python3 scrape_users.py ${ls_opts[@]}
