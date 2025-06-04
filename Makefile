ifeq ($(shell test -e '.env' && echo -n yes),yes)
    include .env
endif

HELP_FUN = \
    %help; \
    while(<>) { \
        push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/; \
    }; \
    print "$$_:\n", map "  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n", @{$$help{$$_}}, "\n" for keys %help;

.PHONY: help env db lint format run test test-cov clean open_db

help: ##@Help Show this help
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

env: ##@Environment Create .env file from example
	@cp -n .env.example .env || true

db: ##@Database Start database with docker-compose
	docker compose up -d --remove-orphans

migrate:  ##@Database Do all migrations in database
	python -m alembic upgrade head

run: ##@Application Run application
	python -m src.main

clean: ##@Code Clean project artifacts
	rm -rf `find . -name __pycache__`
	rm -rf .pytest_cache .coverage htmlcov

%:
	@: