include mk/header.mk

dist_root_$(d)="/ipfs/QmYpvspyyUWQTE226NFWteXYJF3x3br25xmB6XzEoqfzyv"

$(d)/gx: $(d)/gx-v0.13.0
$(d)/gx-go: $(d)/gx-go-v1.7.0

TGTS_$(d) := $(d)/gx $(d)/gx-go
DISTCLEAN += $(wildcard $(d)/gx-v*) $(wildcard $(d)/gx-go-v*) $(d)/tmp

PATH := $(realpath $(d)):$(PATH)

# add by Nigel
FILE = "bin/tmp/gx.tar.gz"
FILE2 = "bin/tmp/gx-go.tar.gz"

exist = $(shell if [ -f $(FILE) ]; then echo "exist"; else echo "notexist"; fi;)
exist2 = $(shell if [ -f $(FILE2) ]; then echo "exist"; else echo "notexist"; fi;)
# add by Nigel

$(TGTS_$(d)):
	rm -f $@$(?exe)
ifeq ($(WINDOWS),1)
	cp $^$(?exe) $@$(?exe)
else
	ln -s $(notdir $^) $@
endif

bin/gx-v%:
	@echo "installing gx $(@:bin/gx-%=%)"
# modified by Nigel
ifeq ($(exist), exist)
	@echo "file already exists"
else
	bin/dist_get $(dist_root_bin) gx $@ $(@:bin/gx-%=%)
endif


bin/gx-go-v%:
	@echo "installing gx-go $(@:bin/gx-go-%=%)"
ifeq ($(exist2), exist)
	@echo "file already exists"
else
	@bin/dist_get $(dist_root_bin) gx-go $@ $(@:bin/gx-go-%=%)
endif
# modified by Nigel

CLEAN += $(TGTS_$(d))
include mk/footer.mk
