// Integer adaptation of the original one-sided ray/segment intersection.
// Reject outside the finite ray before division; all products fit 32 bits.
static int32_t signed_product(int32_t a,int32_t b){
 uint32_t x=a<0?-a:a,y=b<0?-b:b;
 uint32_t p=(x|y)<65536UL?mul16(x,y):x*y;
 return (a<0)!=(b<0)?-(int32_t)p:(int32_t)p;
}
static int32_t dot_raw(const vector2&a,const vector2&b){
 return (signed_product(a.X.raw,b.X.raw)+signed_product(a.Y.raw,b.Y.raw))/4096;
}
Fixed maths::ray_intersect_line(const ray_type& ray,line_type& line){
 int32_t den=-dot_raw(line.PerpendicularC,ray.Direction);
 if(den<=0)return Fixed::bits(INT32_MAX);
 int32_t plane=dot_raw(line.PerpendicularC,ray.Origin)-line.PlaneC.raw;
 uint32_t maximum=mul16(ray.MaxDistance.raw,den)>>12;
 uint32_t minimum=mul16(ray.MinDistance.raw,den)>>12;
 if(plane<-(int32_t)minimum||plane>(int32_t)maximum)return Fixed::bits(INT32_MAX);
 uint32_t mag=plane<0?-plane:plane;
 int32_t distance=mag?((mag<<12)/(uint16_t)den):0;
 if(plane<0)distance=-distance;
 line.RayIntersect.X=Fixed::bits(ray.Origin.X.raw+signed_product(distance,ray.Direction.X.raw)/4096);
 line.RayIntersect.Y=Fixed::bits(ray.Origin.Y.raw+signed_product(distance,ray.Direction.Y.raw)/4096);
 Fixed testPoint=line.Direction.X!=0?line.RayIntersect.X:line.RayIntersect.Y;
 return testPoint>=line.MinCoord&&testPoint<=line.MaxCoord?Fixed::bits(distance):Fixed::bits(INT32_MAX);
}
