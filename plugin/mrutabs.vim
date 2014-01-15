pyfile keys.py
nnoremap <c-Tab> :py mrutabs_nextTab()<Cr>
nnoremap <c-s-Tab> :py mrutabs_prevTab()<Cr>
autocmd TabLeave * py mrutabs_onLeavingTab()
autocmd TabEnter * py mrutabs_onEnteredTab()
