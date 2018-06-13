#!/usr/bin/env bats

ENV_TOOLKIT=${ENV_TOOLKIT-env-toolkit}

@test "dump generates a valid json" {
    run $ENV_TOOLKIT dump
    [ "$status" -eq 0 ]
    echo "$output" | jq .
}

@test "dumps to a file" {
    run $ENV_TOOLKIT dump -f env_write.json
    [ "$status" -eq 0 ]
    jq . env_write.json
}

@test "does not overwrite" {
    run $ENV_TOOLKIT dump -f env_write.json
    [ "$status" -eq 1 ]
}

@test "loads from a file" {
    $ENV_TOOLKIT load -f env_write.json HOME > home_var_file
    grep -q '^export HOME=.\+' home_var_file
}

@test "loads from a file (no-export)" {
    $ENV_TOOLKIT load -f env_write.json --no-export HOME > home_var_file_no_export
    grep -q '^HOME=.\+' home_var_file_no_export
}

@test "can force overwrite" {
    export MYTEST="this_is_a_test"
    export MYTEST1="this_is_a_test1"
    export MYTEST2="this_is_a_test2"
    export MYTEST3="this_is_a_test3"

    run $ENV_TOOLKIT dump --force -f env_write.json
    [ "$status" -eq 0 ]
    jq . env_write.json
}

@test "can load using eval" {
    eval "$($ENV_TOOLKIT load -f env_write.json MYTEST)"
    [ "$MYTEST" = "this_is_a_test" ]
}

@test "can select patterns" {
    eval "$($ENV_TOOLKIT load -f env_write.json --regex ^MYTEST1$)"
    [ "$MYTEST1" = "this_is_a_test1" ]
    [ -z "$MYTEST2" ]
    [ -z "$MYTEST3" ]

    eval "$($ENV_TOOLKIT load -f env_write.json --regex ^MYTEST)"
    [ "$MYTEST1" = "this_is_a_test1" ]
    [ "$MYTEST2" = "this_is_a_test2" ]
    [ "$MYTEST3" = "this_is_a_test3" ]
}

@test "can select patterns (no-export)" {
    eval "$($ENV_TOOLKIT load --no-export -f env_write.json --regex MYTEST1)"
    [ "$MYTEST1" = "this_is_a_test1" ]
    [ -z "$MYTEST2" ]
    [ -z "$MYTEST3" ]

    eval "$($ENV_TOOLKIT load --no-export -f env_write.json --regex ^MYTEST)"
    [ "$MYTEST1" = "this_is_a_test1" ]
    [ "$MYTEST2" = "this_is_a_test2" ]
    [ "$MYTEST3" = "this_is_a_test3" ]
}

@test "can select multiple values (regex)" {
    run $ENV_TOOLKIT load -f env_write.json --regex '^MYTEST\d'

    [ `echo "$output" | wc -l` = 3 ]
    echo "$output" | grep -q "^export MYTEST1=this_is_a_test1$"
    echo "$output" | grep -q "^export MYTEST2=this_is_a_test2$"
    echo "$output" | grep -q "^export MYTEST3=this_is_a_test3$"
}

@test "can select multiple values" {
    run $ENV_TOOLKIT load -f env_write.json MYTEST1 MYTEST2 MYTEST3

    [ `echo "$output" | wc -l` = 3 ]
    echo "$output" | grep -q "^export MYTEST1=this_is_a_test1$"
    echo "$output" | grep -q "^export MYTEST2=this_is_a_test2$"
    echo "$output" | grep -q "^export MYTEST3=this_is_a_test3$"
}

@test "works with weird chars" {
    weird="
    one two
    three '
    four
    "

    export WEIRD_VAR="$weird"
    run $ENV_TOOLKIT dump --force -f env_write.json
    [ "$status" -eq 0 ]

    unset WEIRD_VAR

    eval "$($ENV_TOOLKIT load --no-export -f env_write.json WEIRD_VAR)"
    [ "$WEIRD_VAR" = "$weird" ]
}
