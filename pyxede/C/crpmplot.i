%module crpmplot

%typemap(in) (double *, int){
  int i;
  if (!PySequence_Check($input)) {
    PyErr_SetString(PyExc_ValueError,"Expected a sequence");
    return NULL;
  }
  $2 = PySequence_Length($input);
  $1 = (double *) malloc( ($2) * sizeof(double*) * 2);
  for (i = 0; i < $2; i++) {
    PyObject *x, *y;
    PyObject *cur = PySequence_GetItem($input,i);
    x = PySequence_GetItem(cur,0);
    y = PySequence_GetItem(cur,1);
    if (PyNumber_Check(x) && PyNumber_Check(y)) {
      $1[i]    = (double) PyFloat_AsDouble(x);
      $1[i+$2] = (double) PyFloat_AsDouble(y);
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
  if($1){
    int size = 0; //(int)$1[0];
    $result = PyList_New(size);
    for(i = 0; i < size; i++) {
      int base = (i+1);
      PyObject *valx1 = PyFloat_FromDouble((double) $1[base]);      
      PyObject *valy1 = PyFloat_FromDouble((double) $1[base +   arg2]);      
      PyObject *valx2 = PyFloat_FromDouble((double) $1[base + 2*arg2]);      
      PyObject *valy2 = PyFloat_FromDouble((double) $1[base + 3*arg2]);      
      PyObject *cur  = PyTuple_New(4);
      PyTuple_SetItem(cur, 0,  valx1);
      PyTuple_SetItem(cur, 1,  valy1);
      PyTuple_SetItem(cur, 2,  valx2);
      PyTuple_SetItem(cur, 3,  valy2);
      PyList_SetItem($result, i, cur);
     
    }
    free($1);
  }
  else{
    $result = Py_None;
  }
}

extern double * plot_points(double *, int, int, int, int, int, int, int);
