" Vim syntax file for Jay
if exists("b:current_syntax")
  finish
endif

syn keyword jayKeyword if else for while return func class import try catch main
syn keyword jayType int float string bool
syn keyword jayConstant true false null
syn match jayNumber "\v<\d+(\.\d+)?>"
syn match jayComment "#.*$"
syn region jayString start='"' end='"'

hi def link jayKeyword Keyword
hi def link jayType Type
hi def link jayConstant Constant
hi def link jayNumber Number
hi def link jayComment Comment
hi def link jayString String

let b:current_syntax = "jay"
