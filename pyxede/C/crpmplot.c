#include <stdio.h>

double * plot_points(double *data,int n,int xmin,int ymin,int xscale,int yscale, int offset,int height){
  int i, j=1;
  double last[2];
  double *result = (double *) malloc(sizeof(double)*4*n);

  return NULL;



  last[0] = (data[0] - xmin) * xscale + offset;
  last[1] = (data[n] - ymin) * yscale;
  last[1] = height - last[1];

  for (i=1; i<n; i++){
    double cur[2];
    cur[0] = data[i];
    cur[0] = (cur[0] - xmin) * xscale + offset;
    
    if ((cur[0] - last[0]) > 1.0){
      cur[1] = data[i + n];
      cur[1] = (cur[1] - ymin) * yscale;
      cur[1] = height - cur[1];
      
      result[j]       = last[0];
      result[j +   n] = last[1];
      result[j + 2*n] =  cur[0];
      result[j + 3*n] =  cur[1];
      j++;

      last[0] = cur[0];
      last[1] = cur[1];
    }

  }
  result[0] = j-1;
  return result;

}
