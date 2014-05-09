%module savgol

%typemap(in) (double *, unsigned int) {
  int i;
  if (!PySequence_Check($input)) {
    PyErr_SetString(PyExc_ValueError,"Expected a sequence");
    return NULL;
  }
  $2 = PySequence_Length($input);
  $1 = (double *) malloc(($2)*sizeof(double));
  for (i = 0; i < $2; i++) {
    PyObject *o = PySequence_GetItem($input,i);
    if (PyNumber_Check(o)) {
      $1[i] = (double) PyFloat_AsDouble(o);
    } else {
      PyErr_SetString(PyExc_ValueError,"Sequence elements must be numbers");      
      free($1);
      return NULL;
    }
  }
}
%typemap(freearg) (double *, unsigned int ) {
   if ($1) free($1);
}
%typemap(out) double * {
        int i;
	$result = PyList_New(arg2);
	if($1){
	  for(i = 0; i < arg2; i++) {
	    PyObject *o = PyFloat_FromDouble((double) $1[i]);
	    PyList_SetItem($result,i,o);
	  }
	  free($1);
	}
}
extern double *smooth(double *, unsigned int, unsigned int, int);
