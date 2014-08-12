default:
	@echo "Local examples:"
	@echo "    make run        # Starts a Flask development server locally."
	@echo "    make shell      # Runs 'manage.py shell' locally with iPython."
	@echo "    make celery     # Runs one development Celery worker with Beat."
	@echo "    make style      # Check code styling with flake8."
	@echo "    make lint       # Runs PyLint."
	@echo "    make test       # Tests entire application with pytest."

run:
	(((i=0; while \[ $$i -lt 40 \]; do sleep 0.5; i=$$((i+1));\
	  netstat -anp tcp |grep "\.5000.*LISTEN" &>/dev/null && break; done) &&\
	  open http://localhost:5000/) &)
	./manage.py devserver

