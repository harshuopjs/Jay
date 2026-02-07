module.exports = grammar({
    name: 'jay',

    rules: {
        source_file: $ => repeat($._statement),

        _statement: $ => choice(
            $.function_definition,
            $.class_definition,
            $.import_statement,
            $.main_definition,
            $.if_statement,
            $.while_statement,
            $.for_statement,
            $.try_statement,
            $.return_statement,
            $.expression_statement,
            $.comment
        ),

        function_definition: $ => seq(
            'func',
            $.identifier,
            $.parameter_list,
            $.block
        ),

        class_definition: $ => seq(
            'class',
            $.identifier,
            optional(seq(':', $.identifier)),
            $.block
        ),

        parameter_list: $ => seq(
            '(',
            commaSep($.identifier),
            ')'
        ),

        block: $ => seq(
            '{',
            repeat($._statement),
            '}'
        ),

        if_statement: $ => seq(
            'if', '(', $.expression, ')', $.block,
            optional(seq('else', choice($.block, $.if_statement)))
        ),

        // ... Simplified, extensive rules would follow ...

        identifier: $ => /[a-zA-Z_][a-zA-Z0-9_]*/,
        number: $ => /\d+(\.\d+)?/,
        string: $ => seq('"', /[^"]*/, '"'),
        comment: $ => token(choice(
            seq('#', /.*/),
            seq('/*', /[^*]*\*+([^/*][^*]*\*+)*/, '/')
        ))
    }
});

function commaSep(rule) {
    return optional(seq(rule, repeat(seq(',', rule))));
}
