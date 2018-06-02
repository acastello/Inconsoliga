.PHONY: ligaturize
ligaturize: Inconsoliga-Regular.sfd
	./CreateAllLigatures.sh

Inconsoliga-Regular.ttf: Inconsoliga-Regular.sfd
	fontforge -c "'Open($$1); Generate($$2)'" $^ $@

