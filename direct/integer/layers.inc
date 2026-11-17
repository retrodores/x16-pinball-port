// Separate platform adaptation of TRamp::Collision/FieldEffect. Original
// initialized planes and masks are exported without changing upstream methods.
static uint16_t best_id, crossed[16];
static uint8_t crossed_count;
static bool already_crossed(uint16_t id){
 for(uint8_t i=0;i<crossed_count;++i)if(crossed[i]==id)return true;
 return false;
}
static void cross_ramp(uint16_t id,const vector2& p){
 struct Ramp {uint8_t action,mask,zflag,pad;vector3 plane;vector2 force;Fixed drag,z;};
 static_assert(sizeof(Ramp)==32,"ramp record ABI");
 Ramp m;read_record(44+(id>>6),(id&63)*128+72,&m,sizeof m);
 if(crossed_count<16)crossed[crossed_count++]=id;
 ball.Position.X=p.X;ball.Position.Y=p.Y;
 if(m.action==1){ball.on_ramp=true;ball.offset=m.plane;ball.ramp_force=m.force;ball.ramp_drag=m.drag;ball.CollisionMask=m.mask;}
 else if(m.action>=2){ball.on_ramp=false;ball.CollisionMask=m.mask;if(m.zflag)ball.Position.Z=ball_radius+m.z;}
 if(ball.on_ramp)ball.Position.Z=ball.Position.X*ball.offset.X+ball.Position.Y*ball.offset.Y+ball_radius+ball.offset.Z;
}
